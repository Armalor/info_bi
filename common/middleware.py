from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.background import BackgroundTask
from datetime import datetime

# Локальный импорт:
import sys
from pathlib import Path
__root__ = Path(__file__).absolute().parent.parent.parent.__str__()
sys.path.append(__root__)
from api.users import UserModel
from common.background import DatabaseLogger
from api.logs.models.logs import HitModel
# ~Локальный импорт


class LoggingMiddleware(BaseHTTPMiddleware):

    def __init__(self, app):
        super().__init__(app)

        self.database_logger = DatabaseLogger()

    async def dispatch(self, request: Request, call_next: callable):

        # В качестве времени хита берем время старта обработки.
        hit_timestamp = datetime.today()

        response = await call_next(request)

        # ВНИМАНИЕ! До этой точки (когда уже есть response) request.session недоступен!
        user = UserModel(**request.session.get('user', {}))
        content_type = response.headers.get('content-type', None)
        # if not ('image' in content_type or 'text/css' in content_type):

        hit = HitModel(
            hit_timestamp=hit_timestamp,

            user_id=user.user_id,
            user_login=user.user_login,
            user_ip=request.client.host,
            user_admin_allow=user.user_admin_allow,
            user_regions=user.user_regions,
            user_roles_esia=user.user_roles_esia,

            request_method=request.method,
            request_path=request.url.path,
            response_status_code=response.status_code,
            response_content_type=content_type,
        )

        response.background = BackgroundTask(self.database_logger, hit)

        return response
