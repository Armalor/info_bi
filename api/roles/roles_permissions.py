from itertools import groupby
from fastapi import Request, HTTPException, status
import logging
from aiopg.sa import Engine
from aiopg.sa.result import ResultProxy
from datetime import date
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from typing import Union, Type, List, Dict
from pprint import pprint
from psycopg2 import OperationalError
from fastapi import Depends

# Локальный импорт:
import sys
from pathlib import Path
__root__ = Path(__file__).absolute().parent.parent.parent.__str__()
sys.path.append(__root__)
#
from api.roles.models.role import (
    RolePermissionModel,
    RolePermissionRequestModel,
    RolePermissionViewModel,
    PermissionModel
)
from common.controller import CommonController
# ~Локальный импорт

logger = logging.getLogger("uvicorn.default")

router = InferringRouter()


@cbv(router)
class RolesPermissions(CommonController):

    def __init__(self, *args, **kwargs) -> None:

        super().__init__(*args, **kwargs)

        self.common_model: Type[RolePermissionRequestModel] = RolePermissionRequestModel
        self.table: str = self.common_model.TABLE

    @router.get("/list")
    async def list(self) -> List[Dict]:
        """ Список ролей (всех) с их разрешениями (если есть) """

        roles_with_permissions = list()
        try:
            async with self.engine.acquire() as conn:
                async with conn.begin():
                    _SEL_ROLES = f"""select * from admin.roles order by role_name"""
                    roles_proxy: ResultProxy = await conn.execute(_SEL_ROLES)

                    _SEL_PERMISSIONS = f"""
                        select 
                            rp.role_id, rp.perm_id, rp.roleperm_allow, 
                            p.mod_id, p.mact_id, p.mmod_id, p.perm_name                          
                        from admin.roles_permissions rp
                        join admin.permissions p using (perm_id)
                        order by rp.role_id
                    """
                    perms_proxy: ResultProxy = await conn.execute(_SEL_PERMISSIONS)
                    # Метод «groupby» возвращает итератор, отдающий пары вида Ключ: Итератор.
                    # ВНИМАНИИЕ! Если вместо пары «k: list(v)» отдать по ключу просто итератор «k: v»,
                    # то итератор вернет потому пустой список при конечной обработке.
                    permissions = {k: list(v) for k, v in groupby(await perms_proxy.fetchall(), lambda x: x.role_id)}

                    async for role in roles_proxy:
                        role = dict(role)
                        role['role_permissions'] = permissions.get(role['role_id'])
                        roles_with_permissions.append(role)

        except HTTPException as error:
            raise error
        except Exception as error:

            error = str(error)
            logger.critical(error)

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error,
            )

        return roles_with_permissions

    @router.get("/service_view")
    async def get_service_view(self, mmod_id: str = None):# -> Dict[str, List[RolePermissionViewModel]]:
        """
        Для данного сервиса (для всех сервисов, если mmod_id пустой) возвращаем список ролей (вообще всех ролей)
        с правами по признаку mact_id = 'view'. По сути мы тут для каждого сервиса показываем, какая роль его видит.

        Ответ выглядит так:
        {
            mmod_id: [
                {'role_id': 1, 'role_name': 'Имя роли #1', 'perm_id': 1, 'roleperm_allow': True, ...},
                {'role_id': 2, 'role_name': 'Имя роли #2', 'perm_id': 2, 'roleperm_allow': False, ...},
                ...
                {'role_id': N, 'role_name': 'Имя роли #N', 'perm_id': None, 'roleperm_allow': False, ...},
            ],
            ...
        }
        'roleperm_allow' всегда True или False, null не пихаем.
        """

        params = {
            'mod_id': 'services',
            'mact_id': 'view',
        }

        if mmod_id is not None:
            params['mmod_id'] = mmod_id

        _WHERE = ' and '.join(map(lambda x: f'{x} = %({x})s', params))

        async with self.engine.acquire() as conn, conn.begin():
            proxy: ResultProxy = await conn.execute(
                f"""
                    select 
                        r.role_id, r.role_name, 
                        rp.perm_id, coalesce(rp.roleperm_allow, false) as roleperm_allow, 
                        p.mod_id, p.mact_id, p.mmod_id
                    from admin.roles r
                    cross join admin.permissions p
                    left join admin.roles_permissions rp using (perm_id, role_id)
                    where {_WHERE}
                    order by mmod_id, role_name
                """,
                params
            )

            # permissions = await proxy.fetchall()
            # pprint(permissions)

            permissions = {
                k: [RolePermissionViewModel(**r) for r in v]
                for k, v in groupby(await proxy.fetchall(), lambda x: x.mmod_id)
            }

        return permissions

    @router.post("/service_view")
    async def set_service_view(
        self,
        roles_permissions_list: List[Union[RolePermissionRequestModel, RolePermissionModel]]
    ) -> List[RolePermissionModel]:

        out_roles_permissions_list = []

        async with self.engine.acquire() as conn, conn.begin():
            for roles_permissions in roles_permissions_list:
                try:

                    # Можем сразу пихать запрос только если прямо задано perm_id:
                    if roles_permissions.perm_id is not None:
                        roles_permissions = RolePermissionModel(**roles_permissions.dict())
                    else:
                        # Выставляем фиксированный module action id, тут у нас история только про права на просмотр:
                        roles_permissions.mod_id = 'services'
                        roles_permissions.mact_id = 'view'
                        # roles_permissions.mmod_id не может быть пустым, иначе не пройдет валидацию входных параметров

                        proxy: ResultProxy = await conn.execute(
                            """
                                select * from admin.permissions where 
                                    mod_id = %(mod_id)s and 
                                    mact_id = %(mact_id)s and 
                                    mmod_id = %(mmod_id)s
                            """,
                            roles_permissions.dict()
                        )

                        permission = await proxy.fetchone()
                        if permission is None:
                            raise HTTPException(
                                status_code=status.HTTP_404_NOT_FOUND,
                                detail="для mod_id = '{mod_id}', mact_id = '{mact_id}', mmod_id = '{mmod_id}' не нашли запись в таблице admin.permissions".format(**roles_permissions.dict()),
                            )
                        permission = PermissionModel(**permission)

                        roles_permissions.perm_id = permission.perm_id
                        roles_permissions = RolePermissionModel(**roles_permissions.dict())

                    proxy: ResultProxy = await conn.execute(*roles_permissions.INSERT)

                    out_roles_permissions_list.append(RolePermissionModel(**await proxy.fetchone()))

                except HTTPException as error:
                    raise error
                except Exception as error:
                    error = str(error)
                    logger.critical(error)

                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=error,
                    )

        return out_roles_permissions_list
