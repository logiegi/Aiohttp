# # Асинхронный
#
# from aiohttp import web
#
# from settings import AIOHTTP_PORT
#
# from models import engine, Base, Session
#
# from handlers_ad import AdView
# from handlers_user import UserView
# from handler_hello_world import hello_world
#
#
# async def orm_context(app: web.Application):
#     print('START')
#     # первая миграция:
#     async with engine.begin() as connect:
#         await connect.run_sync(Base.metadata.create_all)
#     yield
#     await engine.dispose()
#     print('SHUT DOWN')
#
#
# @web.middleware
# async def session_middleware(request: web.Request, handler):
#     async with Session() as session:
#         request['session_from_middleware'] = session
#         response = await handler(request)
#         return response
#
#
# app = web.Application()
# app.cleanup_ctx.append(orm_context)
# app.middlewares.append(session_middleware)
#
#
# app.add_routes([
#     web.get('/', hello_world),
#     web.post('/', hello_world),
#
#     web.post('/user/', UserView),
#     # передадим регулярку, которой user_id должен соответствовать
#     # ожидаем цифры от одной и более
#     web.get(r'/user/{user_id:\d+}', UserView),
#     web.patch(r'/user/{user_id:\d+}', UserView),
#     web.delete(r'/user/{user_id:\d+}', UserView),
#
#     web.post('/ad/', AdView),
#     web.get(r'/ad/{ad_id:\d+}', AdView),
#     web.patch(r'/ad/{ad_id:\d+}', AdView),
#     web.delete(r'/ad/{ad_id:\d+}', AdView)
# ])
#
#
# # точка входа ( как у asyncio.run(main) )
# web.run_app(app, host='0.0.0.0', port=AIOHTTP_PORT)

from aiohttp import web
from settings import AIOHTTP_PORT, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
from sqlalchemy.ext.asyncio import create_async_engine
from models import engine, Base, Session
from handlers_ad import AdView
from handlers_user import UserView
from handler_hello_world import hello_world

async def test_db_connection():
    """Проверяем соединение с базой данных перед запуском сервера."""
    test_engine = create_async_engine(f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    try:
        async with test_engine.connect() as conn:
            await conn.execute("SELECT 1")
            print("Database connected successfully.")
    except Exception as e:
        print("Database connection failed:", str(e))
        raise
    finally:
        await test_engine.dispose()

async def orm_context(app: web.Application):
    """Контекст для работы с ORM (инициализация базы)."""
    print('START ORM CONTEXT')
    await test_db_connection()  # Проверяем подключение к базе данных.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
    print('SHUT DOWN ORM CONTEXT')

@web.middleware
async def session_middleware(request: web.Request, handler):
    """Middleware для передачи сессии в запрос."""
    async with Session() as session:
        request['session_from_middleware'] = session
        response = await handler(request)
        return response

def create_app():
    """Создание и настройка приложения."""
    app = web.Application()
    app.cleanup_ctx.append(orm_context)
    app.middlewares.append(session_middleware)

    app.add_routes([
        web.get('/', hello_world),
        web.post('/', hello_world),

        web.post('/user/', UserView),
        web.get(r'/user/{user_id:\d+}', UserView),
        web.patch(r'/user/{user_id:\d+}', UserView),
        web.delete(r'/user/{user_id:\d+}', UserView),

        web.post('/ad/', AdView),
        web.get(r'/ad/{ad_id:\d+}', AdView),
        web.patch(r'/ad/{ad_id:\d+}', AdView),
        web.delete(r'/ad/{ad_id:\d+}', AdView)
    ])
    return app

if __name__ == '__main__':
    app = create_app()
    print("Starting application...")
    web.run_app(app, host='0.0.0.0', port=AIOHTTP_PORT)
