from app import create_app
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler('error.log', maxBytes=100000, backupCount=3)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
handler.setFormatter(formatter)


app = create_app()
app.logger.addHandler(handler)
app.logger.setLevel(logging.DEBUG)

if __name__ == '__main__':
    app.run()