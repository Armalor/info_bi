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

print(f'Получаем список ролей:')
url = f"{host}/api/roles/list"

print(f'GET {url}')

response = session.get(
    url,
    headers=headers,
    auth=auth,
    verify=False,
)

print(response.status_code)

content = response.content.decode()
json_content = json.loads(content)
pprint(json_content, width=255)


# Добавляем новую роль — отсутствует параметр role_id:
data = {
    'role_name': '00 Test Role'
}

url = f"{host}/api/roles/edit"

print(f'Добавляем новую роль:')
print(f'POST {url}')

response = session.post(
    url,
    headers=headers,
    auth=auth,
    json=data,
    verify=False,
)

print(response.status_code)

content = response.content.decode()
json_content = json.loads(content)
pprint(json_content, width=255)

print(f'Получаем список ролей:')
url = f"{host}/api/roles/list"

print(f'GET {url}')

response = session.get(
    url,
    headers=headers,
    auth=auth,
    verify=False,
)

print(response.status_code)

content = response.content.decode()
json_content_1 = json.loads(content)
pprint(json_content_1, width=255)


# Редактируем существующую роль :

data = json_content
data['role_name'] = data['role_name'] + ' (rewrite role name)'

url = f"{host}/api/roles/edit"
print(f'Редактируем существующую роль:')
print(f'POST {url}')

response = session.post(
    url,
    headers=headers,
    auth=auth,
    json=data,
    verify=False,
)

print(response.status_code)

content = response.content.decode()
json_content = json.loads(content)
pprint(json_content, width=255)

# Удаляем роль:

url = f"{host}/api/roles/delete/{json_content['role_id']}"
print(f'Удаляем существующую роль:')
print(f'POST {url}')

response = session.post(
    url,
    headers=headers,
    auth=auth,
    verify=False,
)

print(response.status_code)

content = response.content.decode()
json_content = json.loads(content)
pprint(json_content, width=255)

print(f'Получаем список ролей:')
url = f"{host}/api/roles/list"

print(f'GET {url}')

response = session.get(
    url,
    headers=headers,
    auth=auth,
    verify=False,
)

print(response.status_code)

content = response.content.decode()
json_content_1 = json.loads(content)
pprint(json_content_1, width=255)