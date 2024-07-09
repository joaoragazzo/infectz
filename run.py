import logging
from logging.handlers import RotatingFileHandler
import sys

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


file_handler = RotatingFileHandler('early_error.log', maxBytes=500000, backupCount=3)
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


logger.debug('Logger configurado. Testando a escrita no arquivo de log.')


for handler in logger.handlers:
    handler.flush()

try:
    from app import create_app
    logger.debug('Módulo app importado com sucesso. Tentando criar a aplicação...')
    app = create_app()
    logger.debug('Aplicação criada com sucesso.')
except Exception as e:
    logger.exception("Erro ao criar a aplicação: ")
    for handler in logger.handlers:
        handler.flush()
    raise

for handler in logger.handlers:
    handler.flush()

if __name__ == '__main__':
    logger.debug('Iniciando a aplicação...')
    app.run()