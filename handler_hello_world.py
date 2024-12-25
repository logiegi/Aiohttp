# Асинхронный

from aiohttp import web

async def hello_world(request: web.Request):
    json_data = await request.json()
    # headers = request.headers
    # qs = request.query
    return web.json_response({
        "Hello": "world",
        'json': json_data
    })