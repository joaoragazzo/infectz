import os


class Config:
    SECRET_KEY = f"{os.urandom(45)}"
    # sdk = mercadopago.SDK('TEST-4895180949334138-052121-b1da13509c6cdc1959dc03a74cb2c0ec-1566496776')
    MERCADO_PAGO_SDK_KEY = 'TEST-4895180949334138-052121-b1da13509c6cdc1959dc03a74cb2c0ec-1566496776'
    STEAM_API_KEY = "E41C0983D3EDF0DCD85BD43D0B0E5FCB"
    SERVER_SITE_URL = "https://d0f3-187-86-102-199.ngrok-free.app"  # Obs: Não colocar a '/' no final
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@localhost/infectz"
    SQLALCHEMY_TRACK_MODIFICATIONS = False