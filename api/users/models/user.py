import json
from pydantic import Field, validator
from typing import Optional, Union, ClassVar, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from pydantic.typing import AbstractSetIntStr, MappingIntStrAny

# Локальный импорт:
import sys
from pathlib import Path
__root__ = Path(__file__).absolute().parent.parent.parent.parent.__str__()
sys.path.append(__root__)

from common.model import CommonModel
# ~Локальный импорт


class UserModel(CommonModel):

    TABLE: ClassVar[str] = 'admin.users'
    PKEY: ClassVar[set] = {'user_id'}
    ON_CONFLICT: ClassVar[str] = f"""
        (user_login) do update set 
        user_last_login_time = EXCLUDED.user_last_login_time,
        -- поля, приходяшие из ЕСИА:
        user_comment = EXCLUDED.user_comment,
        user_regions = EXCLUDED.user_regions,
        user_roles_esia = EXCLUDED.user_roles_esia
    """

    user_id: int = Field(default=None)
    user_login: str = Field(default=None)
    user_password_hash: str = Field(default=None, )
    user_outer: bool = Field(default=None)
    user_registered: datetime = Field(default=datetime.now())
    user_comment: str = Field(default=None)
    user_admin_allow: bool = Field(default=False)
    user_last_login_time: datetime = Field(default=datetime.now())
    user_regions: list = Field(default=None)
    user_roles_esia: list = Field(default=None)

    @staticmethod
    def _parse_timestring(user_timestring):
        if isinstance(user_timestring, str):

            user_timestring = user_timestring.strip('"')[:19]

            for time_format in ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"]:
                try:
                    user_timestring = datetime.strptime(user_timestring, time_format)
                except ValueError:
                    pass
                else:
                    break

        return user_timestring

    @validator("user_registered", pre=True)
    def parse_user_registered(cls, user_registered):
        return UserModel._parse_timestring(user_registered)

    @validator("user_last_login_time", pre=True)
    def parse_user_last_login_time(cls, user_last_login_time):
        return UserModel._parse_timestring(user_last_login_time)

    def dumps(self, exclude: Optional[Union['AbstractSetIntStr', 'MappingIntStrAny']] = {'user_password_hash'}) -> dict:
        """Здесь нам нужны пустые значения, т.к. этот метод используется для формирования первичного ключа"""
        return super().dumps(exclude=exclude)

    @property
    def FIND_BY_LOGIN(self) -> tuple:
        return f'''select * from {self.TABLE} as t where t.user_login = %(user_login)s''', self.dict()

    @property
    def FIND_ROLES_BY_USER_ID(self):
        return f'''
            select r.* 
            from admin.roles r 
            join admin.users_roles ur using (role_id) 
            join admin.users u on (user_id)
            where u.user_id = %(user_id)s
        ''', self.dict()