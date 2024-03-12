import requests
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
    # session_cookie = config.session_cookie
    # session.cookies.set('session', session_cookie)

print(f'Получаем текущего пользователя:')
url = f"{host}/api/users/current?user_login=121-437-603 19"  # Гордеев
# url = f"{host}/api/users/current?user_login=451-437-582 82"  # Админ Ролевич_Портал Тестовый

print(f'GET {url}')

response = session.get(
    url,
    headers=headers,
    auth=auth,
    verify=False,
    allow_redirects=False
)

print(response.status_code)
if 200 != response.status_code:
    exit(1)


content = response.content.decode()
json_content = json.loads(content)
pprint(json_content, width=255)
