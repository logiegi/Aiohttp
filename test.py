import asyncio

async def test_connection():
    from sqlalchemy.ext.asyncio import create_async_engine
    from settings import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME

    engine = create_async_engine(f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
            print("Database connection successful.")
    except Exception as e:
        print("Database connection failed:", e)
    finally:
        await engine.dispose()

asyncio.run(test_connection())