import os
import random
from requests.auth import HTTPBasicAuth
import pytest
from attrdict import AttrDict
from typing import Dict, Callable, Optional
import requests
from datetime import datetime, timedelta
import json
import urllib3
from pprint import pprint

# Локальный импорт:
import sys
from pathlib import Path
__root__ = Path(__file__).absolute().parent.parent.__str__()

from config import Config
Config(__root__)  # Сразу инициализируем конфиг для pytest
# ~Локальный импорт


@pytest.fixture(autouse=True, scope='function')
def disable_warnings() -> None:
    """ Глушим warning «InsecureRequestWarning: Unverified HTTPS request is being made to host...»
        NB! Если фикстура не возвращает значения, то она дергается каждым включающим ее тестом автоматически.
        1. Здесь это малоприменимо, т.к. данная конкретная фикстура подключается через autouse.
        2. Любой другой scope, кроме function, не дает эффекта.
    """
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@pytest.fixture
def config() -> AttrDict:
    """ Выдача (заранее подгруженного) конфига состояний; отдаем сразу attrdict """
    config = Config(__root__).config
    return config


@pytest.fixture
def headers() -> dict:
    """ Выдача заголовков для POST-запросов """
    headers = {"content-type": "application/json"}

    return headers


@pytest.fixture
def auth(config) -> Optional[HTTPBasicAuth]:
    """ Выдача заголовков для POST-запросов """

    if config.server_type == 'local':
        admin = config.users[0]
        auth = HTTPBasicAuth(admin.login, admin.password)
    else:
        auth = None

    return auth


@pytest.fixture
def post_request(config, headers, auth) -> Callable[[str, Dict], None]:
    def request(routing, data):

        host = config.server_url

        url = f"{host}/{routing}"

        response = requests.post(
            url,
            headers=headers,
            auth=auth,
            json=data,
            verify=False,
            allow_redirects=False,
            timeout=4,
        )

        assert 200 == response.status_code and 'OK' == response.reason

    return request
