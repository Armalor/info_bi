from aiopg.sa.result import ResultProxy

# Локальный импорт:
import sys
from pathlib import Path
__root__ = Path(__file__).absolute().parent.parent.__str__()
sys.path.append(__root__)
from lifespan import Lifespan
from api.logs.models.logs import HitModel
# ~Локальный импорт


class DatabaseLogger:
    def __init__(self):
        self.engine = Lifespan.get_engine()

    async def __call__(self, hit: HitModel):
        # print('BACKGROUND:', hit.request_method, hit.request_path, hit.response_status_code, hit.user_id, hit.user_login)
        async with Lifespan.get_engine().acquire() as conn, conn.begin():
            await conn.execute(*hit.INSERT)

