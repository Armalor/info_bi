import logging
from abc import ABC, abstractmethod
from aiopg.sa import Engine, SAConnection
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from fastapi import Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import Union, Any, ClassVar, Type, Dict, get_type_hints, Optional
from pprint import pprint


# Локальный импорт:
import sys
from os import path
__path__ = path.dirname(path.abspath(__file__))
__parent__ = path.abspath(path.join(__path__, ".."))
# Добавляем в sys-path именно __parent__, чтобы не слетала настройка в PyCharm
sys.path.append(__parent__)
from config import Config
from dependencies import Dependencies
from lifespan import Lifespan
from api.users import UserModel
# ~Локальный импорт

# Здесь нужен __path__, т.к. вообще хз, откуда будет запускаться uvicorn
logger = logging.getLogger("uvicorn.default")

router = InferringRouter()


@cbv(router)
class CommonController(ABC):

    DB_CONFIG_KEY: ClassVar[str] = 'db_147_portal'

    def __init__(self, user: UserModel = Depends(Dependencies.get_user)) -> None:

        self.config = Config().config

        self.templates = Jinja2Templates(directory="template_and_static_simlink")
        self.static = StaticFiles(directory="template_and_static_simlink")

        self.engine: Engine = Lifespan.get_engine(self.DB_CONFIG_KEY)

        self.user: UserModel = user
