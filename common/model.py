import json
from pydantic import BaseModel
from typing import Optional, Union, ClassVar, TYPE_CHECKING
from enum import IntEnum, Enum
from pprint import pprint

if TYPE_CHECKING:
    from pydantic.typing import AbstractSetIntStr, MappingIntStrAny


class SortDirectionEnum(str, Enum):
    asc = 'asc'
    desc = 'desc'


class StateIdEnum(IntEnum):
    """
    Класс идентификаторов статуса создаваемых объектов

    draft = 1  Черновик

    needs_improvement = 2  Требует доработки

    awaits_review = 10  Ожидает проверки редактором

    publish = 100  Опубликовано
    """

    draft = 1  # Черновик
    needs_improvement = 2  # Требует доработки
    awaits_review = 10  # Ожидает проверки редактором
    publish = 100  # Опубликовано


class CommonModel(BaseModel):
    """
    Обобщенные параметры модели: таблица, первичный ключ, действие при конфликте в INSERT и сам INSERT.
    """

    TABLE: ClassVar[str] = None
    PKEY: ClassVar[set] = None
    # Для ON CONFLICT DO NOTHING объект_конфликта может не указываться; в этом случае игнорироваться будут
    # все конфликты с любыми ограничениями (и уникальными индексами).
    # Для ON CONFLICT DO UPDATE объект_конфликта должен указываться.
    ON_CONFLICT: ClassVar[str] = 'do nothing'

    def dumps(self, exclude: Optional[Union['AbstractSetIntStr', 'MappingIntStrAny']] = None) -> dict:
        return json.loads(self.json(exclude=exclude))

    @property
    def INSERT(self):

        cols = self.dict(exclude=self.PKEY).keys()

        placeholders = map(lambda x: f'%({x})s', cols)

        _insert = f'''
            insert into {self.TABLE} ({', '.join(cols)}) values ({', '.join(placeholders)})
            on conflict {self.ON_CONFLICT} 
            returning {self.TABLE}.*
        '''

        return _insert, self.dict()

    @property
    def UPDATE(self):

        cols = self.dict(exclude=self.PKEY).keys()

        placeholders = map(lambda x: f'{x} = %({x})s', cols)

        pkey = map(lambda x: f'{x} = %({x})s', self.PKEY)

        _update = f'''
            update {self.TABLE} set
                {', '.join(placeholders)}
            where 
                {' and '.join(pkey)}
            returning {self.TABLE}.*
        '''

        return _update, self.dict()

    @property
    def DELETE(self):

        pkey = map(lambda x: f'{x} = %({x})s', self.PKEY)

        _delete = f'''
            delete from {self.TABLE}
            where 
                {' and '.join(pkey)}
            returning {self.TABLE}.*
        '''

        return _delete, self.dict()
