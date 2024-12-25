import asyncio

import aiohttp

from settings import AIOHTTP_HOST, AIOHTTP_PORT


URL = f'http://{AIOHTTP_HOST}:{AIOHTTP_PORT}'


async def result(response):
    print(response.method, response.url)
    data = ''
    try:
        data = await response.json()
    except Exception as err:
        print(err)
        data = await response.text()
    finally:
        print(data, '\n===============\n')
    return data


async def main():
    async with aiohttp.ClientSession() as session:
        response = await session.get(URL + '/')
        await result(response)

        response = await session.post(URL + '/',
            json={
                'json_key': 'json_value'
            },
            params={
                'qs_key_1': 'qs_value_1'  # query string
            },
            headers={
                'token': 'some_token'
            }
        )
        await result(response)
        #   читаем json от сервера
        # data = await response.json()
        # print(data)  # должен прийти словарик {'Hello': 'world'}


        #********************************************
        response = await session.post(URL + '/user/',
            json={
                'username': 'user_222',
                'password': '23456789',
                'email': 'u22@ya.ru'
            },
            params={}, headers={}
        )
        await result(response)


        #********************************************
        response = await session.patch(URL + '/user/1',
            json={
                'username': 'new_name',
                'password': '12345677',
                'email': 'u112@ya.ru'
            },
            params={}, headers={}
        )
        await result(response)


        #********************************************
        response = await session.get(URL + '/user/1')
        await result(response)


        #********************************************
        response = await session.post(URL + '/ad/',
            json={"user_id": "1"})
        await result(response)


        #********************************************
        response = await session.patch(URL + '/ad/1',
            json={'header': 'new_header'}
        )
        await result(response)


        #********************************************
        response = await session.get(URL + '/ad/1')
        await result(response)





asyncio.run(main())