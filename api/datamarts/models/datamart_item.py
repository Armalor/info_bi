from pydantic import Field
from typing import Optional, List, ClassVar
from datetime import datetime

# Локальный импорт:
import sys
from pathlib import Path
__root__ = Path(__file__).absolute().parent.parent.parent.parent
sys.path.append(__root__.__str__())

from common.model import CommonModel, StateIdEnum
# ~Локальный импорт


class DatamartItemModel(CommonModel):
    """
    Модель витрины данных, представление datamarts.items.
    """

    TABLE: ClassVar[str] = 'datamarts.items'
    PKEY: ClassVar[set] = {'item_id'}

    item_id: int = Field(default=None)
    user_id: int = Field(default=None)
    state_id: StateIdEnum = Field(default=StateIdEnum.publish)
    item_added: datetime = Field(default=datetime.now())
    item_modified: datetime = Field(default=datetime.now())
    # item_version: int = Field(default=1) При update приходит некорректная версия, пока исключим этот параметр
    item_comment: str = Field(default=None)

    item_signature: str = Field()
    item_title: str = Field()
    item_description: str = Field(default=None)
    item_tables_cnt: int = Field(default=None)
    item_link_pg_admin: str = Field(default=None)
    item_link_saud: str = Field(default=None)


class DatamartItemDeleteModel(DatamartItemModel):
    item_signature: str = Field(default=None)
    item_title: str = Field(default=None)
