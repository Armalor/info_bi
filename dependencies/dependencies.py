from fastapi import HTTPException, status, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing_extensions import Annotated
from typing import Optional, Union
import secrets
import asyncio
import logging
from aiopg.sa.result import ResultProxy
from psycopg2 import OperationalError

from pprint import pprint

# Локальный импорт:
import sys
from pathlib import Path
__root__ = Path(__file__).absolute().parent.parent.__str__()
sys.path.append(__root__)
from config import Config
from esia import Client
from lifespan import Lifespan
from api.users.models.user import UserModel
from api.logs.models.logs import UserSessionModel
# ~Локальный импорт

config = Config(__root__).config
security = HTTPBasic()
logger = logging.getLogger("uvicorn.default")


class Dependencies:

    client: Client = Client(config.client)

    @staticmethod
    def get_auth():
        return Dependencies.basic_auth if config.server_type == 'local' else Dependencies.ESIA_auth

    @staticmethod
    async def basic_auth(request: Request, credentials: Annotated[HTTPBasicCredentials, Depends(security)]):

        if 'user' not in request.session and request.url.path not in ['/logout', '/callback']:
            engine = Lifespan.get_engine()
            try:
                async with engine.acquire() as conn, conn.begin():
                    _SQL = """
                        update admin.users set user_last_login_time = now() 
                            where user_login = %(login)s and user_password_hash = md5(%(password)s)
                        returning admin.users.*
                    """
                    proxy: ResultProxy = await conn.execute(_SQL, {'login': credentials.username, 'password': credentials.password})

                    user = await proxy.fetchone()

                    if user:
                        await Dependencies.set_user(request, user)

                    else:
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect email or password",
                            headers={"WWW-Authenticate": "Basic"},
                        )

            except OperationalError as error:
                error = str(error)
                logger.critical(error)
                return {'error': error}

    @staticmethod
    async def ESIA_auth(request: Request):
        # Если пользователя нет в текущей сессии и это не возврат из ЕСИА, то требуем сначала залогиниться:

        if 'user' not in request.session and request.url.path not in ['/logout', '/callback']:

            login_url = Dependencies.get_login_url(request)

            raise HTTPException(
                status_code=status.HTTP_302_FOUND,
                detail="Authentication required",
                headers={"Location": login_url},
            )

    @staticmethod
    async def set_user(request: Request, user: Union[dict, UserModel, None]) -> Optional[dict]:
        if user is not None:

            user = UserModel(**(user.dict() if isinstance(user, UserModel) else user))

            request.session['user'] = user.dumps()

            # Полагаем, что set_user происходит только при старте сессии
            engine = Lifespan.get_engine()
            async with engine.acquire() as conn, conn.begin():
                user_session = UserSessionModel(
                    user_id=user.user_id,
                    user_login=user.user_login,
                    user_admin_allow=user.user_admin_allow,
                    user_regions=user.user_regions,
                    user_roles_esia=user.user_roles_esia,

                    session_ip=request.client.host,
                    session_login_time=user.user_last_login_time,
                    session_logout_time=None,
                    session_id=None
                )

                await conn.execute(*user_session.INSERT)

        return request.session.get('user', None)

    @staticmethod
    def get_user(request: Request) -> Optional[UserModel]:
        user = request.session.get('user', {})
        user = UserModel(**user)
        return user

    @staticmethod
    def get_login_url(request: Request):

        provided_scopes = request.query_params.get("scope")
        default_scopes = Dependencies.client.config['scope']
        scopes = provided_scopes if provided_scopes else default_scopes

        login_url = Dependencies.client.get_authn_req_url(
            dict(request.session),
            request.query_params.get("acr", None),
            request.query_params.get("forceAuthN", False),
            scopes,
            request.query_params.get("forceConsent", False),
            request.query_params.get("allowConsentOptionDeselection", False),
            request.query_params.get("responseType", "code"),
            request.query_params.get("ui_locales"),
            request.query_params.get("max_age"),
            request.query_params.get("claims"),
            config.client.get("send_parameters_via", "query_string")
        )

        return login_url

