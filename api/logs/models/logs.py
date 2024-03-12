from pydantic import Field
from typing import ClassVar, List, Tuple, Union
from datetime import datetime, date
from enum import Enum

# Локальный импорт:
import sys
from pathlib import Path
__root__ = Path(__file__).absolute().parent.parent.parent.parent.__str__()
sys.path.append(__root__)

from common.model import CommonModel
# ~Локальный импорт


class HitModel(CommonModel):

    """
    Модель записи лога хитов, таблица hits
    """

    TABLE: ClassVar[str] = 'logs.hits'

    hit_timestamp: datetime = Field(default=datetime.today())

    user_id: int = Field(default=None)
    user_login: str = Field(default=None)
    user_ip: str = Field(default=None)
    user_admin_allow: bool = Field(default=None)
    user_regions: list = Field(default=None)
    user_roles_esia: list = Field(default=None)

    request_method: str = Field()
    request_path: str = Field()
    response_status_code: int = Field()
    response_content_type: str = Field(default=None)


class HitSearchModel(HitModel):
    hit_timestamp: datetime = Field(default=None)

    hit_date: date = Field(default=None)
    hit_date_from: date = Field(default=None)
    hit_date_to: date = Field(default=None)

    request_method: str = Field(default=None)
    request_path: str = Field(default=None)
    response_status_code: int = Field(default=None)


    @property
    def INSERT(self):

        cols = self.dict(exclude=self.PKEY).keys()

        placeholders = map(lambda x: f'%({x})s' if x != 'user_login' else f'md5(%({x})s)', cols)

        _insert = f'''
            insert into {self.TABLE} ({', '.join(cols)}) values ({', '.join(placeholders)})
            on conflict {self.ON_CONFLICT} 
            returning {self.TABLE}.*
        '''

        return _insert, self.dict()


class UserSessionModel(CommonModel):

    TABLE: ClassVar[str] = 'logs.users_sessions'

    user_id: int = Field()
    user_login: str = Field()
    user_admin_allow: bool = Field(default=None)
    user_regions: list = Field(default=None)
    user_roles_esia: list = Field(default=None)

    session_ip: str = Field(default=None)
    session_login_time: datetime = Field(default=datetime.today())
    session_logout_time: datetime = Field(default=None)
    session_id: str = Field(default=None)
