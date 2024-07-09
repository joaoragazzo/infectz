import logging
from logging.handlers import RotatingFileHandler
import sys

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

file_handler = RotatingFileHandler('early_error.log', maxBytes=10000, backupCount=3)
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

logger.debug('Logger configurado. Iniciando a criação da aplicação...')

try:
    from app import create_app
    app = create_app()
except Exception as e:
    logger.exception("Erro ao criar a aplicação: ")
    raise

if __name__ == '__main__':
    app.run()