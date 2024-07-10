import logging
from logging.handlers import RotatingFileHandler
import sys

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

file_handler = RotatingFileHandler('error.log', maxBytes=500000, backupCount=3)
file_handler.setLevel(logging.ERROR)
file_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

logger.debug('Logger configurado. Testando a escrita no arquivo de log.')


for handler in logger.handlers:
    handler.flush()

try:
    from app import create_app
    app = create_app()
except Exception as e:
    for handler in logger.handlers:
        handler.flush()
    raise

for handler in logger.handlers:
    handler.flush()

if __name__ == '__main__':
    app.run()