from pydantic import Field
from typing import ClassVar, List

# Локальный импорт:
import sys
from pathlib import Path
__root__ = Path(__file__).absolute().parent.parent.parent.parent.__str__()
sys.path.append(__root__)

from common.model import CommonModel
# ~Локальный импорт


class RoleModel(CommonModel):
    """ Модель данных для ролей admin.roles """

    TABLE: ClassVar[str] = 'admin.roles'
    PKEY: ClassVar[set] = {'role_id'}
    ON_CONFLICT: ClassVar[str] = f"""(role_id) do update set
         role_name = EXCLUDED.role_name, 
         role_description = EXCLUDED.role_description
    """

    role_id: int = Field(default=None)
    role_name: str = Field()
    role_description: str = Field(default=None)

    @property
    def FIND_BY_NAME(self) -> tuple:
        return f'''select * from {self.TABLE} as t where t.role_name = %(role_name)s''', self.dict()


class PermissionModel(CommonModel):
    """
    Модель данных для описания разрешений admin.permissions.

    Разрешение состоит из
    - имени модуля mod_id (например, service);
    - модификатора модуля mmod_id (например, конкретный дашборд «prevent_defects» в сервисах);
    - действия mact_id, на которое выдается разрешение (например, «view» — просмотр);
    - и, наконец, имени разрешения perm_name (например, «Просматривать сервис "Прогнозирование загрузки мощностей"»)
    """

    TABLE: ClassVar[str] = 'admin.permissions'
    PKEY: ClassVar[set] = {'perm_id'}
    ON_CONFLICT: ClassVar[str] = f"""(perm_id) do update set         
        mod_id    = EXCLUDED.mmod_id, 
        mmod_id   = EXCLUDED.mmod_id,
        mact_id   = EXCLUDED.mact_id,
        perm_name = EXCLUDED.perm_name
    """

    perm_id: int = Field()
    mod_id: str = Field()
    mmod_id: str = Field()
    mact_id: str = Field()
    perm_name: str = Field()


class RolePermissionModel(CommonModel):
    """
    Базовая модель для разрешений на роли admin.roles_permissions.

    Связывает роли и разрешения к ним.
    """

    TABLE: ClassVar[str] = 'admin.roles_permissions'
    PKEY: ClassVar[set] = set()  # {'role_id', 'perm_id'} # Убираем первичный ключ, т.к. здесь нет автогенерации ключа.
    ON_CONFLICT: ClassVar[str] = f'(role_id, perm_id) do update set roleperm_allow = EXCLUDED.roleperm_allow'

    role_id: int = Field()
    perm_id: int = Field()
    roleperm_allow: bool = Field(default=False)


class RolePermissionRequestModel(RolePermissionModel):
    """
    Модель прав на роль для POST-запроса API к service_view.

    Здесь perm_id необязательный параметр, его пытаемся найти через пару mact_id и mmod_id.
    """

    perm_id: int = Field(default=None)

    # Этих параметров нет в таблице admin.roles_permissions,
    # сюда их включаем как элементы, присылаемые методом API.
    mod_id: str = Field(default='services')
    mact_id: str = Field(default='view')
    mmod_id: str = Field()  # mmod_id тут задает сигнатуру сервиса, обязательный параметр


class RolePermissionViewModel(RolePermissionRequestModel):
    """ Используется в GET-запросе к service_view, здесь нам нужно имя роли в ответе. """

    role_name: str = Field()

