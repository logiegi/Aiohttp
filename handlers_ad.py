# Асинхронный

from aiohttp import web

from typing import Type
import json
from sqlalchemy.ext.asyncio import AsyncSession

from models import Session, Ad
from validate_scheme import CreateAd, PatchAd

from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError


JSON_TYPE = 'application/json'


async def validate(json_data: dict,
             model_class: Type[CreateAd] | Type[PatchAd]):
    try:
        model_item = model_class(**json_data)
        return model_item.model_dump(exclude_none=True)
    except ValidationError as err:
        errHTTP = web.HTTPBadRequest
        errMSG = err.errors()[0]
        text = json.dumps({
            "status": str(errHTTP.status_code),  # 400
            "message": f"{errMSG['msg']} ({errMSG['input']})"
        })
        raise errHTTP(text=text, content_type=JSON_TYPE)


async def get_ad(ad_id: int, session: Session) -> Ad:
    ad = await session.get(Ad, ad_id)
    if ad is None:
        errHTTP = web.HTTPNotFound
        text = json.dumps({
            "status": errHTTP.status_code,  # 404
            "message": f"ad id={ad_id} not found"
        })
        raise errHTTP(text=text, content_type=JSON_TYPE)
    return ad


class AdView(web.View):
    @property
    def ad_id(self) -> int:
        return int(self.request.match_info['user_id'])

    @property
    def session(self) -> AsyncSession:
        return self.request['session_from_middleware']

    async def get(self):                                        # НАЙТИ
        ad = await get_ad(self.ad_id, self.session)
        response = web.json_response(ad.info_dict())
        return response

    async def post(self):                                       # ДОБАВИТЬ
        json_data = await self.request.json()
        json_data = await validate(json_data, CreateAd)

        new_ad = Ad(**json_data)
        self.session.add(new_ad)
        try:
            await self.session.commit()
        except IntegrityError as err:
            errHTTP = web.HTTPConflict
            text = json.dumps({
                "status":   str(errHTTP.status_code),  # 409
                "message":  f'ad already exists with the same data   {err}'
            })
            raise errHTTP(text=text, content_type=JSON_TYPE)
        return web.json_response({
                "status": "advertisement add success",
                "id": new_ad.id
        })

    async def patch(self):                                    # ДОБАВИТЬ
        json_data = await self.request.json()
        json_data = await validate(json_data, CreateAd)

        ad = await get_ad(self.ad_id, self.session)
        for field, value in json_data.items():
            setattr(ad, field, value)
        try:
            await self.session.commit()
        except IntegrityError as err:
            errHTTP = web.HTTPConflict
            errMSG = err
            text = json.dumps({
                "status":   str(errHTTP.status_code),  # 409
                "message":  f"Patch: unknown trouble..."
                            f"  pgcode={errMSG.orig.pgcode}   {err}"
            })
            raise errHTTP(text=text, content_type=JSON_TYPE)
        return web.json_response({
                "status": "advertisement patch success",
                "id": ad.id
        })

    async def delete(self):
        ad = await get_ad(self.ad_id, self.session)
        await self.session.delete(ad)
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
            "ad": ad.info_dict()
        })