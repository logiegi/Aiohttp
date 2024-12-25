import pydantic  # содержит СХЕМЫ ВАЛИДАЦИИ

import requests as requests
from typing import Optional

from settings import AIOHTTP_HOST, AIOHTTP_PORT

URL = f'http://{AIOHTTP_HOST}:{AIOHTTP_PORT}'


def err_short_password(password: str, min_lenght: int = 8) -> str:
    err = f"passwortd short: less than {min_lenght} signs!"
    return err if len(password) < min_lenght else ''


def err_not_a_user(user_id: int) -> str:
    err = 'user not found...'
    response = requests.get(f'{URL}/user/{user_id}')
    return err if response.status_code != 200 else ''


class CreateUser(pydantic.BaseModel):  # здесь будет валидация пользователя
    # (того, что пойдет в post)
    username: str  # два обязательных поля:
    password: str  # то, что должен прислать клиент!
    email: Optional[str] = 'missing@email'

    # Можно добавить валидации, напр, проверять сложность пароля

    @pydantic.field_validator('password')
    def validate_password(cls, value):
        # cls               -   класс, value - значение
        # password          -   валидируемое поле
        # validate_password -   так можем давать название методам валидации
        error = err_short_password(value)
        if error:
            raise ValueError(error)
            # нужно выбросить исключение именно ValueError,
            # и библ. pydantic его правльно обработает!
        return value
        # возвращаем уже валидированное значение
        # (иногда здесь хешируют пароль, но лучше делать отдельно!)


class PatchUser(pydantic.BaseModel):
    username: Optional[str] = None  # поля опциональны
    password: Optional[str] = None  # (не обязательно все обновлять...)
    email: Optional[str] = None

    @pydantic.field_validator('password')
    def validate_password(cls, value):
        error = err_short_password(value)
        if error:
            raise ValueError(error)
        return value


class CreateAd(pydantic.BaseModel):  # валидация новой рекламы
    user_id: int
    header: Optional[str] = 'made ad'
    description: Optional[str] = None

    @pydantic.field_validator('user_id')
    def validate_user_id(cls, value):
        error = err_not_a_user(value)
        if error:
            raise ValueError(error)
        return value


class PatchAd(pydantic.BaseModel):  # валидация рекламы
    user_id: Optional[int] = None
    header: Optional[str] = None
    description: Optional[str] = None

    @pydantic.field_validator('user_id')
    def validate_user_id(cls, value):
        error = err_not_a_user(value)
        if error:
            raise ValueError(error)
        return value