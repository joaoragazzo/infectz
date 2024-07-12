import os
from dotenv import load_dotenv


class Config:
    load_dotenv()
    SECRET_KEY = f"{os.urandom(45)}"

    MERCADO_PAGO_SDK_KEY = os.getenv('MERCADO_PAGO_SDK_KEY')
    MERCADO_PAGO_PUBLIC_KEY = os.getenv('MERCADO_PAGO_PUBLIC_KEY')
    MERCADO_PAGO_CLIENT_ID = os.getenv('MERCADO_PAGO_CLIENT_ID')
    MERCADO_PAGO_CLIENT_SECRET = os.getenv('MERCADO_PAGO_CLIENT_SECRET')
    MERCADO_PAGO_WEBHOOK_SIGNATURE = os.getenv('MERCADO_PAGO_WEBHOOK_SIGNATURE')

    STEAM_API_KEY = os.getenv('STEAM_API_KEY')
    SERVER_SITE_URL = "https://infectz.0x6a70.com"

    DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_POOL_TIMEOUT = 30
    SQLALCHEMY_POOL_RECYCLE = 1800
    SQLALCHEMY_MAX_OVERFLOW = 20

    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = 3600
