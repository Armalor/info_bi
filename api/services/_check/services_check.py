import requests
from requests import Response
from datetime import datetime, timedelta
import json
from requests.auth import HTTPBasicAuth
from pprint import pprint
from itsdangerous import base64_decode

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Локальный импорт:
import sys
from pathlib import Path
__root__ = Path(__file__).absolute().parent.parent.parent.parent.__str__()
sys.path.append(__root__)
# Добавляем в sys-path именно __parent__, чтобы не слетала настройка в PyCharm
sys.path.append(__root__)
from config import Config
from api.services.models.service_item import ServiceItemModel
from common.model import StateIdEnum
# ~Локальный импорт

config = Config(__root__).config
host = config.server_url

headers = {"content-type": "application/json"}

session = requests.session()

if config.server_type == 'local':
    auth = HTTPBasicAuth(config.users[0].login, config.users[0].password)
else:
    auth = None
    # Довольно грязный хак: выставляем cookie от реально существующей сессии с реальным пользователем admin.
    session_cookie = config.session_cookie
    session.cookies.set('session', session_cookie)


def print_response(response: Response):
    print(response.status_code)
    if 200 == response.status_code:
        content = response.content.decode()
        json_content = json.loads(content)
        pprint(json_content, width=255)
    else:
        print(response.text)


def services_list():
    print(f'Получаем список сервисов:')
    url = f"{host}/api/services/list"

    print(f'GET {url}')

    _response = session.get(
        url,
        headers=headers,
        auth=auth,
        verify=False,
        allow_redirects=False
    )

    print_response(_response)


# services_list()

###
###
###
def services_edit(item_id=None):
    if item_id:
        print(f'Редактируем сервис item_id={item_id}:')
    else:
        print(f'Добавляем новый сервис:')
    url = f"{host}/api/services/edit"
    print(f'POST {url}')

    service = ServiceItemModel(
        item_id=item_id,

        user_id=1,
        state_id=StateIdEnum.needs_improvement,
        item_title=f'Тестируем создание и редактирование сервиса item_id={"new" if not item_id else item_id}',
        item_description='Тестовый сервис 32',
        item_signature='test_signature'
    )

    response = session.post(
        url,
        headers=headers,
        auth=auth,
        json=service.dumps(),
        verify=False,
    )

    print_response(response)


def services_delete(item_id):
    print(f'Удаляем сервис item_id={item_id}:')

    url = f"{host}/api/services/delete/{item_id}"
    print(f'POST {url}')

    response = session.post(
        url,
        headers=headers,
        auth=auth,
        verify=False,
    )

    print_response(response)


services_edit(32)
# services_delete(32)
