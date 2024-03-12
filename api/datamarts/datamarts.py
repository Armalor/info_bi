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
from api.datamarts.models.datamart_item import DatamartItemModel, DatamartItemDeleteModel
# ~Локальный импорт

logger = logging.getLogger("uvicorn.default")

router = InferringRouter()


@cbv(router)
class Datamarts(CommonController):

    def __init__(self, *args, **kwargs) -> None:

        super().__init__(*args, **kwargs)

        self.table: str = 'datamarts.items'
        self.common_model: Type[DatamartItemModel] = DatamartItemModel

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
                        from datamarts.items t
                        left join (
                            select array_agg (distinct mmod_id::text) as viewable
                            from admin.users_roles r
                            join admin.roles_permissions rp  using (role_id)
                            join admin.permissions p using (perm_id)
                            where user_id = %(user_id)s
                            and mod_id = 'datamarts'
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
    async def edit(self, datamart: DatamartItemModel) -> Union[DatamartItemModel, Dict]:

        try:
            async with self.engine.acquire() as conn:
                async with conn.begin():
                    if datamart.item_id is None:
                        _SQL, params = datamart.INSERT
                    else:
                        _SQL, params = datamart.UPDATE

                    proxy: ResultProxy = await conn.execute(_SQL, params)

                    _datamart = await proxy.fetchone()

                    if _datamart:
                        datamart = DatamartItemModel(**_datamart)
                    else:
                        raise OperationalError(f'Витрина не найдена: item_id={datamart.item_id}')

        except OperationalError as error:
            error = str(error)
            logger.critical(error)

            return {'error': error}

        return datamart

    @router.post("/delete/{item_id}")
    async def delete(self, item_id: int):

        datamart = DatamartItemDeleteModel(item_id=item_id)
        try:
            async with self.engine.acquire() as conn:
                async with conn.begin():

                    proxy: ResultProxy = await conn.execute(*datamart.DELETE)

                    _deleted = await proxy.fetchone()

                    if _deleted:
                        deleted = DatamartItemModel(**_deleted)
                    else:
                        raise OperationalError(f'Витрина не найдена: item_id={datamart.item_id}')

        except OperationalError as error:
            error = str(error)
            logger.critical(error)

            return {'error': error}

        return deleted
