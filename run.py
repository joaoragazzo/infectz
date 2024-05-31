from app import create_app
import logging
from logging.handlers import RotatingFileHandler

app = create_app()


handler = RotatingFileHandler('error.log', maxBytes=10000, backupCount=3)
handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
handler.setFormatter(formatter)
app.logger.addHandler(handler)

if __name__ == '__main__':
    app.run(debug=True)