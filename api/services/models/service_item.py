from pydantic import Field
from typing import Optional, List, ClassVar
from datetime import datetime

# Локальный импорт:
import sys
from pathlib import Path
__root__ = Path(__file__).absolute().parent.parent.parent.parent.__str__()
sys.path.append(__root__)

from common.model import CommonModel, StateIdEnum
# ~Локальный импорт


class ServiceItemModel(CommonModel):
    """
    Модель сервиса, представление services.items.
    """

    TABLE: ClassVar[str] = 'services.items'
    PKEY: ClassVar[set] = {'item_id'}

    item_id: int = Field(default=None)
    user_id: int = Field(default=None)
    state_id: StateIdEnum = Field(default=StateIdEnum.publish)
    item_added: datetime = Field(default=datetime.now())
    item_modified: datetime = Field(default=datetime.now())
    # item_version: int = Field(default=1) При update приходит некорректная версия, пока исключим этот параметр
    item_comment: str = Field(default=None)
    item_type: str = Field(default='dashboard')
    item_signature: str = Field()
    item_title: str = Field()
    item_description: str = Field(default=None)
    item_link: str = Field(default=None)


class ServiceItemDeleteModel(ServiceItemModel):
    item_signature: str = Field(default=None)
    item_title: str = Field(default=None)
