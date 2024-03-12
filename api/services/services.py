from abc import ABC

from fastapi import Request
import logging
from aiopg.sa import Engine
from aiopg.sa.result import ResultProxy
from datetime import date
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from typing import Union, Type, Dict
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
from dependencies import Dependencies
from api.services.models.service_item import ServiceItemModel, ServiceItemDeleteModel
# ~Локальный импорт

logger = logging.getLogger("uvicorn.default")

router = InferringRouter()


@cbv(router)
class Services(CommonController):

    def __init__(self, *args, **kwargs) -> None:

        super().__init__(*args, **kwargs)

        self.table: str = 'services.items'
        self.common_model: Type[ServiceItemModel] = ServiceItemModel

    @router.get("/list")
    async def list(self, request: Request):
        """ Получить список существующих сервисов с учетом прав на просмотр """
        try:

            async with self.engine.acquire() as conn:
                async with conn.begin():
                    _SEL = f"""
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

                    proxy: ResultProxy = await conn.execute(_SEL, self.user.dict())

                    items = [{k: v for k, v in i.items()} for i in await proxy.fetchall()]

        except OperationalError as error:
            error = str(error)
            logger.critical(error)

            return {'error': error}

        return {'items': items}

    @router.post("/edit")
    async def edit(self, service: ServiceItemModel) -> Union[ServiceItemModel, Dict]:

        try:
            async with self.engine.acquire() as conn:
                async with conn.begin():
                    if service.item_id is None:
                        _SQL, params = service.INSERT
                    else:
                        _SQL, params = service.UPDATE

                    proxy: ResultProxy = await conn.execute(_SQL, params)

                    _service = await proxy.fetchone()

                    if _service:
                        service = ServiceItemModel(**_service)
                    else:
                        raise OperationalError(f'Сервис не найден: item_id={service.item_id}')

        except OperationalError as error:
            error = str(error)
            logger.critical(error)

            return {'error': error}

        return service

    @router.post("/delete/{item_id}")
    async def delete(self, item_id: int):

        service = ServiceItemDeleteModel(item_id=item_id)
        try:
            async with self.engine.acquire() as conn:
                async with conn.begin():

                    proxy: ResultProxy = await conn.execute(*service.DELETE)

                    _deleted = await proxy.fetchone()

                    if _deleted:
                        deleted = ServiceItemModel(**_deleted)
                    else:
                        raise OperationalError(f'Сервис не найден: item_id={service.item_id}')

        except OperationalError as error:
            error = str(error)
            logger.critical(error)

            return {'error': error}

        return deleted
