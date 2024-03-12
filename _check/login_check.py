import requests
from datetime import datetime, timedelta
import json
from pprint import pprint

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Локальный импорт:
import sys
from pathlib import Path
__root__ = Path(__file__).absolute().parent.parent.__str__()
sys.path.append(__root__)
from config import Config
# ~Локальный импорт

config = Config(__root__).config
host = config.server_url


host = config.server_url


url = f"{host}/login"

print(f'GET {url}')

response = requests.get(
    url,
    verify=False,
)

print(response.status_code)

content = response.content.decode()
print(content)

