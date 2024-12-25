from dotenv import load_dotenv
import os

load_dotenv()

DB_ENGINE = os.getenv('DB_ENGINE')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_HOST_PORT')

DSN = f'{DB_ENGINE}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

AIOHTTP_HOST = os.getenv('AIOHTTP_HOST')
AIOHTTP_PORT = os.getenv('AIOHTTP_PORT')