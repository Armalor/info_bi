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


class UserRoleModel(CommonModel):
    """
    Пользователь <-> Роль пользователя, таблица admin.users_roles

    """
    TABLE: ClassVar[str] = 'admin.users_roles'
    PKEY: ClassVar[set] = set()  # {'user_id', 'role_id'} Убираем первичный ключ, т.к. здесь нет автогенерации ключа.
    ON_CONFLICT: ClassVar[str] = f"""
        (user_id, role_id) do update set 
        ur_start = EXCLUDED.ur_start,
        ur_finish = EXCLUDED.ur_finish
    """
    user_id: int = Field()
    role_id: int = Field()
    ur_start: datetime = Field(default=None)
    ur_finish: datetime = Field(default=None)
