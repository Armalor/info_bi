import requests
from datetime import datetime, timedelta
import json
from requests.auth import HTTPBasicAuth
from pprint import pprint

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
from api.roles.models.role import RolePermissionRequestModel, RolePermissionModel
# ~Локальный импорт

config = Config(__root__).config
host = config.server_url

session = requests.session()

headers = {"content-type": "application/json"}

if config.server_type == 'local':
    auth = HTTPBasicAuth(config.users[0].login, config.users[0].password)
else:
    auth = None
    # Довольно грязный хак: выставляем cookie от реально существующей сессии с реальным пользователем admin.
    session_cookie = config.session_cookie
    session.cookies.set('session', session_cookie)


###
###
###
print(f'Задаем права на просмотр сервисов:')
url = f"{host}/api/roles_permissions/service_view"
print(f'POST {url}')

data = list()
data.append(RolePermissionRequestModel(role_id=99, mmod_id='monitoring_of_financial_activities', roleperm_allow=True).dict())  # availability_of_medical_care -> perm_id = 12
data.append(RolePermissionRequestModel(role_id=-3, mmod_id='staffing_management', roleperm_allow=False).dict())  # staffing_management -> perm_id = 12
data.append(RolePermissionModel(role_id=-3, perm_id=11, roleperm_allow=False).dict()) # perm_id = 11 -> monitoring_of_financial_activities

# data.append({'role_id': -3, 'mmod_id': None, 'roleperm_allow': True}) # Этот словарь не пробьется через контроль входных параметров.

response = session.post(
    url,
    headers=headers,
    auth=auth,
    json=data,
    verify=False,
)

print(response.status_code)
if 200 == response.status_code:
    content = response.content.decode()
    json_content = json.loads(content)
    pprint(json_content, width=255)
else:
    print(response.text)


###
###
###
print(f'Получаем список ролей с правами каждой ВООБЩЕ НА ЛЮБОЙ МОДУЛЬ:')
url = f"{host}/api/roles_permissions/list"

print(f'GET {url}')

response = session.get(
    url,
    headers=headers,
    auth=auth,
    verify=False,
)

print(response.status_code)
if 200 == response.status_code:
    content = response.content.decode()
    json_content = json.loads(content)
    pprint(json_content, width=200)
else:
    print(response.text)


###
###
###
print(f'Получаем список ролей с правами ТОЛЬКО НА ПРОСМОТР ТОЛЬКО СЕРВИСОВ (конкретного сервиса):')
url = f"{host}/api/roles_permissions/service_view"

print(f'GET {url}')

response = session.get(
    url,
    headers=headers,
    auth=auth,
    verify=False,
)

print(response.status_code)
if 200 == response.status_code:
    content = response.content.decode()
    json_content = json.loads(content)
    pprint(json_content, width=127)
else:
    print(response.text)


###
###
###
print(f'Получаем список ролей с правами ТОЛЬКО НА ПРОСМОТР КОНКРЕТНОГО СЕРВИСА (availability_of_medical_care):')
url = f"{host}/api/roles_permissions/service_view?mmod_id=monitoring_of_financial_activities"

print(f'GET {url}')

response = session.get(
    url,
    headers=headers,
    auth=auth,
    verify=False,
)

print(response.status_code)
if 200 == response.status_code:
    content = response.content.decode()
    json_content = json.loads(content)
    pprint(json_content, width=127)
else:
    print(response.text)
