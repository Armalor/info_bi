import traceback
from datetime import datetime
from fastapi import HTTPException, status, Request, Path
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
import logging
from jwkest import BadSignature
from jwkest.jwt import JWT
from aiopg.sa.result import ResultProxy
from datetime import date
from typing import ClassVar, Type, Any
from pprint import pprint
from psycopg2 import OperationalError
from fastapi import Depends
from enum import Enum
from uuid import UUID
from fastapi_sessions.backends.implementations import InMemoryBackend

# Локальный импорт:
import sys
from pathlib import Path
__root__ = Path(__file__).absolute().parent.parent.parent.__str__()
sys.path.append(__root__)
#
from config import Config
from common.controller import CommonController
from dependencies import Dependencies
from esia import UserESIAModel
from api.users.models.user import UserModel
from api.users.models.user_role import UserRoleModel
from api.roles.models.role import RoleModel
# ~Локальный импорт

logger = logging.getLogger("uvicorn.default")

router = InferringRouter()


@cbv(router)
class Main(CommonController):

    @router.get('/vite.svg')
    async def vite_svg(self):
        _path = self.static.lookup_path('vite.svg')[0]
        return FileResponse(_path)

    @router.get('/login')
    async def login(self, request: Request):
        login_url = Dependencies.get_login_url(request)
        return RedirectResponse(login_url, status_code=302)

    @router.get('/callback')
    async def callback(self, request: Request, state: str = None, code: str = None):
        session = request.session

        code_verifier = session.get('code_verifier')

        # if 'state' not in session or session['state'].decode() != request.query_params['state']:
        #     print('Missing or invalid state')
        #
        # if "code_verifier" not in session:
        #     print("No code_verifier in session")
        #
        # if not code:
        #     print('No code in response')

        try:
            token_data = Dependencies.client.get_token(code=code, code_verifier=code_verifier)

            user_esia = UserESIAModel()

            if 'access_token' in token_data:
                user_esia.access_token = token_data['access_token']

            if Dependencies.client.jwt_validator is not None and 'id_token' in token_data:
                # validate JWS; signature, aud and iss.
                # Token type, access token, ref-token and JWT
                if 'issuer' not in Dependencies.client.config:
                    logger.error('Could not validate token: no issuer configured')

                if 'audience' in Dependencies.client.config:
                    audience = Dependencies.client.config['audience']
                elif 'template_client' in Dependencies.client.config:
                    audience = Dependencies.client.config['template_client']
                else:
                    audience = Dependencies.client.config['client_id']

                try:
                    Dependencies.client.jwt_validator.validate(token_data['id_token'], Dependencies.client.config['issuer'], audience)
                except BadSignature as bs:
                    logger.error('Could not validate token: %s' % bs.message)
                except Exception as ve:
                    return logger.error("Unexpected exception: %s" % ve.message)

                user_esia.id_token = token_data['id_token']

            if 'refresh_token' in token_data:
                user_esia.refresh_token = token_data['refresh_token']

            if user_esia.access_token:
                user = UserModel(
                    user_login=Dependencies.client.get_snils(user_esia.access_token),
                    user_outer=True,
                    user_comment=Dependencies.client.get_name(user_esia.access_token),
                    user_regions=Dependencies.client.get_regions(user_esia.access_token),
                    user_roles_esia=Dependencies.client.get_roles(user_esia.access_token),
                )

                async with self.engine.acquire() as conn, conn.begin():
                    proxy: ResultProxy = await conn.execute(*user.INSERT)

                    user = UserModel(**await proxy.fetchone())

                # Вызывать set_user можем только выйдя из соединения по созданию пользователя
                await Dependencies.set_user(request=request, user=user)

                if user.user_roles_esia:
                    async with self.engine.acquire() as conn, conn.begin():
                        pprint(user.user_roles_esia)
                        for esia_role_name in user.user_roles_esia:
                            print(esia_role_name)
                            role = RoleModel(role_name=esia_role_name, role_description='Роль из ЕСИА')
                            proxy: ResultProxy = await conn.execute(*role.FIND_BY_NAME)
                            _role = await proxy.fetchone()
                            if _role:
                                role = RoleModel(**_role)
                                print('role matches to:')
                                pprint(role)
                            else:
                                print('role matches to nothing, create:')

                                proxy: ResultProxy = await conn.execute(*role.INSERT)
                                role = RoleModel(**await proxy.fetchone())
                                pprint(role)

                            user_role = UserRoleModel(user_id=user.user_id, role_id=role.role_id)
                            pprint(user_role.dict())
                            proxy: ResultProxy = await conn.execute(*user_role.INSERT)
                            user_role = UserRoleModel(**await proxy.fetchone())
                            print('user_role:')
                            pprint(user_role)

                #
                # atoken = JWT().unpack(user_esia.access_token).payload()
                # print('TOKEN 2:')
                # pprint(atoken)

        except Exception as _err:

            tb = traceback.format_exc()
            msg = 'Error: «{}»\n{}'.format(str(_err).strip(), tb)
            logger.error(msg)

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(_err),
            )

        return RedirectResponse(router.url_path_for('index'), status_code=status.HTTP_302_FOUND)

    @router.get('/logout')
    async def logout(self, request: Request):

        _logout_user = UserModel(**request.session.pop('user', {}))

        logged_out = request.session.pop('logged_out', False)

        if not logged_out:
            if 'local' == self.config.server_type:
                # Это нужно только при локальной авторизации,
                # status.HTTP_401_UNAUTHORIZED не позволяет сразу уйти со страницы.
                request.session['logged_out'] = True

                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Logout",
                    headers={"WWW-Authenticate": "Basic"},
                )
            else:
                end_session_endpoint = Dependencies.client.config['end_session_endpoint']
                logout_request = f'{end_session_endpoint}?client_id={self.config.client.client_id}&post_logout_redirect_uri={self.config.client.base_url}'
        else:
            logout_request = router.url_path_for('index')

        return RedirectResponse(logout_request, status_code=status.HTTP_302_FOUND)

    @router.get("/datamarts")
    @router.get("/information")
    @router.get("/information/table")
    @router.get("/information/table/{table}")
    @router.get("/reports")
    @router.get("/services")
    @router.get("/settings")
    @router.get("/settings")
    @router.get("/user")
    @router.get("/user/application")
    @router.get("/")  # этот роутинг должен идти последним, т.к. url_path_for('index') выбирает именно последний
    async def index(self, request: Request, table: int = None):
        """ Роутинг для всех страниц frontend сразу. """
        user = Dependencies.get_user(request)
        response = HTMLResponse(
            content=self.templates.get_template('index.html').render({
                'user': user
            })
        )

        return response
