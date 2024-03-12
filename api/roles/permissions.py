from abc import ABC

from fastapi import Request, HTTPException, status
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
from api.roles.models.role import PermissionModel
from common.controller import CommonController
# ~Локальный импорт

logger = logging.getLogger("uvicorn.default")

router = InferringRouter()


@cbv(router)
class Permissions(CommonController):

    def __init__(self, *args, **kwargs) -> None:

        super().__init__(*args, **kwargs)

        self.common_model: Type[PermissionModel] = PermissionModel
        self.table: str = self.common_model.TABLE

    @router.get("/list")
    async def list(self, request: Request, mmod_id: str = None):

        print(mmod_id)

        _WHERE_CONDITIONS = {}
        _WHERE = []

        if mmod_id is not None:
            _WHERE_CONDITIONS['mmod_id'] = mmod_id
            _WHERE.append('mmod_id = %(mmod_id)s')

        if _WHERE:
            _WHERE = 'where ' + ' and '.join(_WHERE)
        else:
            _WHERE = ''

        try:
            async with self.engine.acquire() as conn:
                async with conn.begin():
                    _SEL = f"select * from {self.table} {_WHERE} order by mod_id, mact_id, mmod_id"

                    proxy: ResultProxy = await conn.execute(_SEL, _WHERE_CONDITIONS)

                    permissions = [PermissionModel(**i) for i in await proxy.fetchall()]

        except OperationalError as error:
            error = str(error)
            logger.critical(error)

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error,
            )

        return permissions
