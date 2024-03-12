from abc import ABC

from fastapi import Request, HTTPException, status
import logging
from aiopg.sa import Engine
from aiopg.sa.result import ResultProxy
from datetime import date
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from typing import List, Type, Union, Dict, Optional
from pprint import pprint
from psycopg2 import OperationalError
from fastapi import Depends


# Локальный импорт:
import sys
from pathlib import Path
__root__ = Path(__file__).absolute().parent.parent.parent
sys.path.append(__root__.__str__())
#
from api.logs.models.logs import HitModel, HitSearchModel
from common.model import SortDirectionEnum
from common.controller import CommonController
# ~Локальный импорт

logger = logging.getLogger("uvicorn.default")

router = InferringRouter()


@cbv(router)
class Hits(CommonController):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.table: str = 'logs.hits'
        self.common_model: Type[HitModel] = HitModel

    @router.get("/list")
    @router.post("/list")
    async def list(
        self,
        search: Optional[HitSearchModel] = None,
        order_by: str = 'hit_timestamp',
        sort_direction: SortDirectionEnum = SortDirectionEnum.desc,
        limit: int = 100,
        offset: int = 0
    ) -> Union[List[HitModel], Dict]:

        if order_by and order_by not in HitSearchModel().dict():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f'order_by value "{order_by}" not allowed',
            )

        try:
            async with self.engine.acquire() as conn:
                async with conn.begin():
                    _SEL = f"""
                        select * from {self.table} 
                        where true
                        order by {order_by} {sort_direction} 
                        limit {limit} 
                        offset {offset}
                    """

                    proxy: ResultProxy = await conn.execute(_SEL)

                    hits = [HitModel(**i) for i in await proxy.fetchall()]

        except OperationalError as error:
            error = str(error)
            logger.critical(error)

            return {
                'error': error
            }

        return hits
