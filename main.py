from fastapi import FastAPI, Depends
import logging
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles

# Локальный импорт:
import sys
from pathlib import Path
__root__ = Path(__file__).absolute().parent.__str__()
sys.path.append(__root__)

from config import Config
config = Config(__root__).config
from dependencies.dependencies import Dependencies
from lifespan import Lifespan

from api.main.main import router as main_router
from api.roles.roles import router as roles_router
from api.roles.roles_permissions import router as roles_permissions_router
from api.roles.permissions import router as permissions_router
from api.services.services import router as services_router
from api.datamarts.datamarts import router as datamarts_router
from api.users.users import router as users_router
from api.logs.hits import router as hits_router
from common.middleware import LoggingMiddleware
# ~Локальный импорт

logger = logging.getLogger("uvicorn.default")

app_lifespan = Lifespan()

app = FastAPI(lifespan=app_lifespan.lifespan, dependencies=[Depends(Dependencies.get_auth())])
app.add_middleware(SessionMiddleware, secret_key=config.session_secret_key)
app.add_middleware(LoggingMiddleware)

# Такая загадочная структура для статиков обусловлена жестко заданной архитектурой React-проекта для frontend'а:
assets = StaticFiles(directory="template_and_static_simlink/assets")
app.mount("/assets", assets, name="assets")

###
app.include_router(users_router, prefix='/api/users')
app.include_router(roles_router, prefix='/api/roles')
app.include_router(permissions_router, prefix='/api/permissions')
app.include_router(roles_permissions_router, prefix='/api/roles_permissions')
###

###
app.include_router(services_router, prefix='/api/services')
app.include_router(datamarts_router, prefix='/api/datamarts')
###

app.include_router(hits_router, prefix='/api/logs/hits')

app.include_router(main_router)

origins = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

