import logging
from logging.handlers import RotatingFileHandler
import sys

# Configurando o logger raiz
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Configurando o manipulador de arquivo rotativo
file_handler = RotatingFileHandler('early_error.log', maxBytes=10000, backupCount=3)
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Testando o log para garantir que está funcionando
logger.debug('Logger configurado. Testando a escrita no arquivo de log.')

# Forçando a escrita dos logs no disco
for handler in logger.handlers:
    handler.flush()
    handler.close()

#try:
#    from app import create_app
#    app = create_app()
#except Exception as e:
#    logger.exception("Erro ao criar a aplicação: ")
#    raise

#if __name__ == '__main__':
#    app.run()