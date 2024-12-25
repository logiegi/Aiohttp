# Асинхронный

from aiohttp import web

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Type
import json

from models import Session, User
from validate_scheme import CreateUser, PatchUser
from security import md5_hash_password, bcrypt_hash_password

from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError


JSON_TYPE = 'application/json'


async def validate(json_data: dict,
             model_class: Type[CreateUser] | Type[PatchUser]):
    try:
        model_item = model_class(**json_data)
        return model_item.model_dump(exclude_none=True) # чтобы не было None
    except ValidationError as err:
        errHTTP = web.HTTPBadRequest
        errMSG = err.errors()[0]
        # будет список ошибок, полей от библ. pydantic с подробным описанием
        text = json.dumps({
            "status": errHTTP.status_code,  # 400
            "message": f"{errMSG['msg']} ({len(errMSG['input'])})"
        })
        raise errHTTP(text=text, content_type=JSON_TYPE)


async def get_user(user_id: int, session: Session) -> User:
    user = await session.get(User, user_id)
    if user is None:
        errHTTP = web.HTTPNotFound
        text = json.dumps({
            "status": errHTTP.status_code,  # 404
            "message": f"user id={user_id} not found"
        })
        raise errHTTP(text=text, content_type=JSON_TYPE)
    return user


# def get_ad_list_of_user(user_id: int, session: Session) -> list:
#     return list()

# def get_number_of_user_ads(user_id: int, session: Session) -> int:
#     return len(get_user_ads(user_id, session))


class UserView(web.View):
    # request и user_id будем получать из self
    # в request в переменной match_info - список значений,
    # там и user_id

    @property
    def user_id(self) -> int:
        return int(self.request.match_info['user_id'])

    @property
    def session(self) -> AsyncSession:
        return self.request['session_from_middleware']

    async def get(self):                                        # НАЙТИ
        user = await get_user(self.user_id, self.session)
        response = web.json_response(user.info_dict())
        return response

    async def post(self):                                       # ДОБАВИТЬ
        json_data = await self.request.json()
        json_data = await validate(json_data, CreateUser)

        # извлекаем пароль (строку) для хэширования:
        pw: str = json_data["password"]
        # кладем хэш (строку) обратно в json:
        hash_pw = bcrypt_hash_password(pw)
        json_data["password"] = hash_pw
        # json_data["password"] = md5_hash_password(pw)

        new_user = User(**json_data)
        self.session.add(new_user)
        try:
            await self.session.commit()
        except IntegrityError as err:
            errHTTP = web.HTTPConflict
            errMSG = err
            text = json.dumps({
                "status":   str(errHTTP.status_code),  # 409
                "message":  f"Key(username)=({new_user.username})"
                            f" already exists!"
                            f"  pgcode={errMSG.orig.pgcode}"
            })
            raise errHTTP(text=text, content_type=JSON_TYPE)
        return web.json_response({
                "status": f"user '{new_user.username}' add success",
                "id": new_user.id
        })

    async def patch(self):                                      # ИЗМЕНИТЬ
        json_data = await self.request.json()
        json_data = await validate(json_data, CreateUser)
        # если пароль пришел, то хэшируем его:
        if 'password' in json_data:
            json_data["password"] = bcrypt_hash_password(json_data["password"])
            # json_data["password"] = md5_hash_password(json_data["password"])

        user = await get_user(self.user_id, self.session)
        for field, value in json_data.items():
            setattr(user, field, value)
        try:
            await self.session.commit()
        except IntegrityError as err:
            errHTTP = web.HTTPConflict
            errMSG = err
            text = json.dumps({
                "status":   str(errHTTP.status_code),  # 409
                "message":  f"Key(username)=({user.username})"
                            f" is busy!"
                            f"  pgcode={errMSG.orig.pgcode}"
            })
            raise errHTTP(text=text, content_type=JSON_TYPE)
        return web.json_response({
                "status": f"user '{user.username}' patch success",
                "id": user.id
        })

    async def delete(self):                                      # УДАЛИТЬ
        user = await get_user(self.user_id, self.session)
        await self.session.delete(user)
        try:
            await self.session.commit()
        except IntegrityError as err:
            errHTTP = web.HTTPConflict
            errMSG = err
            text = json.dumps({
                "status":   str(errHTTP.status_code),  # 409
                "message":  f"Delete: unknown trouble..."
                            f"  pgcode={errMSG.orig.pgcode}   {err}"
            })
            raise errHTTP(text=text, content_type=JSON_TYPE)
        return web.json_response({
            "status": "user delete success",
            "user": user.info_dict()
        })