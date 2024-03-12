from abc import ABC

from fastapi import Request
import logging
from aiopg.sa import Engine
from aiopg.sa.result import ResultProxy
from datetime import date
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from typing import ClassVar, Type, Any
from pprint import pprint
from psycopg2 import OperationalError
from fastapi import Depends

# Локальный импорт:
import sys
from pathlib import Path
__root__ = Path(__file__).absolute().parent.parent.parent.__str__()
sys.path.append(__root__)
#
from common.controller import CommonController
from api.users import UserModel
# ~Локальный импорт

logger = logging.getLogger("uvicorn.default")

router = InferringRouter()


@cbv(router)
class Users(CommonController):

    def __init__(self, *args, **kwargs) -> None:

        super().__init__(*args, **kwargs)

        self.table: str = 'admin.users'
        self.common_model: Type[UserModel] = UserModel

    @router.get("/current")
    async def current(self, request: Request):
        """ Получить текущего пользователя со всеми правами """
        try:

            async with self.engine.acquire() as conn, conn.begin():
                _SEL_USER = f"""
                    select t.* from admin.users t where user_id = %(user_id)s
                """

                proxy: ResultProxy = await conn.execute(_SEL_USER, self.user.dict())

                db_user = UserModel(**await proxy.fetchone()).dumps()

                _SEL_ITEMS = f"""
                    select 
                        t.*, 
                        array[t.item_signature, 'all'] && perm.viewable as can_view 
                    from services.items t
                    left join (
                        select array_agg (distinct mmod_id::text) as viewable
                        from admin.users_roles r
                        join admin.roles_permissions rp  using (role_id)
                        join admin.permissions p using (perm_id)
                        where user_id = %(user_id)s
                        and mod_id = 'services'
                        and mact_id = 'view'
                        and roleperm_allow = true
                        and now()::date between coalesce(ur_start, now()::date) and coalesce(ur_finish, now()::date) 
                    ) as perm on true
                    order by item_title
                """

                proxy: ResultProxy = await conn.execute(_SEL_ITEMS, self.user.dict())

                items = [{k: v for k, v in i.items()} for i in await proxy.fetchall()]

        except OperationalError as error:
            error = str(error)
            logger.critical(error)

            return {'error': error}

        return {
            'user': db_user,
            'items': items,
        }
