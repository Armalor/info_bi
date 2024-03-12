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
from config import Config
from lifespan import Lifespan
from api.roles.models.role import RoleModel
from common.controller import CommonController
# ~Локальный импорт

logger = logging.getLogger("uvicorn.default")

router = InferringRouter()


@cbv(router)
class Roles(CommonController):

    def __init__(self, *args, **kwargs) -> None:

        super().__init__(*args, **kwargs)

        self.table: str = 'admin.roles'
        self.common_model: Type[RoleModel] = RoleModel

    @router.get("/list")
    async def list(self, request: Request):
        try:
            async with self.engine.acquire() as conn:
                async with conn.begin():
                    _SEL = f"select * from {self.table} order by role_name"

                    proxy: ResultProxy = await conn.execute(_SEL)

                    roles = [{k: v for k, v in i.items()} for i in await proxy.fetchall()]

        except OperationalError as error:
            error = str(error)
            logger.critical(error)

            return {
                'error': error
            }

        return {'roles': roles}

    @router.post("/edit")
    async def edit(self, role: RoleModel):

        if not role.role_id:
            _SQL = f'insert into {self.table} (role_name) values (%(role_name)s) returning {self.table}.*'
        else:
            _SQL = f'update {self.table} set role_name = %(role_name)s where role_id = %(role_id)s returning {self.table}.*'

        try:
            async with self.engine.acquire() as conn:
                async with conn.begin():

                    proxy: ResultProxy = await conn.execute(_SQL, role.__dict__)

                    new_role = await proxy.fetchone()

                    if new_role:
                        new_role = dict(new_role)
                    else:
                        raise OperationalError(f'Роль для редактирования с role_id={role.role_id} не найдена')

        except OperationalError as error:
            error = str(error)
            logger.critical(error)

            return {'error': error}

        return new_role

    @router.post("/delete/{role_id}")
    async def delete(self, role_id: int):

        _SQL = f'delete from {self.table} where role_id = %(role_id)s returning {self.table}.*'

        try:
            async with self.engine.acquire() as conn:
                async with conn.begin():

                    proxy: ResultProxy = await conn.execute(_SQL, {'role_id': role_id})

                    deleted_role = await proxy.fetchone()

                    if deleted_role:
                        deleted_role = dict(deleted_role)
                    else:
                        raise OperationalError(f'Роль для удаления с role_id={role_id} не найдена')

        except OperationalError as error:
            error = str(error)
            logger.critical(error)

            return {'error': error}

        return deleted_role
