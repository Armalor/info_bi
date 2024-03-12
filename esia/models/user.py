from pydantic import Field
from typing import Optional, List
from datetime import datetime

# Локальный импорт:
import sys
from pathlib import Path
__root__ = Path(__file__).absolute().parent.parent.parent.parent.__str__()
sys.path.append(__root__)

# Получается циклический импорт, не могу определить, где именно from api.main.models.user import User as UserModel
from common.model import CommonModel
# ~Локальный импорт


class UserESIA(CommonModel):
    access_token: str = Field(default=None)
    refresh_token: str = Field(default=None)
    id_token: str = Field(default=None)
    access_token_json: dict = Field(default=None)
    id_token_json: dict = Field(default=None)
    name: str = Field(default=None)
    api_response: str = Field(default=None)
    front_end_id_token: str = Field(default=None)
    front_end_id_token_json: dict = Field(default=None)
    front_end_access_token: str = Field(default=None)
