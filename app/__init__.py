from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event, exc
from sqlalchemy.pool import Pool
from run import logger

db: SQLAlchemy = SQLAlchemy()
logger.debug('Point (__init__) #1')

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    logger.debug('Point (__init__) #2')
    app.config.from_object('app.config.Config')
    db.init_app(app)
    logger.debug('Point (__init__) #3')
    @event.listens_for(Pool, "connect")
    def connect(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("SET SESSION wait_timeout = 28800")
        cursor.close()

    logger.debug('Point (__init__) #4')


    @event.listens_for(Pool, "checkout")
    def checkout(dbapi_connection, connection_record, connection_proxy):
        try:
            # Test the connection
            dbapi_connection.cursor().execute("SELECT 1")
        except dbapi_connection.Error as err:
            if err.args[0] in (2006, 2013, 2014, 2045, 2055):
                connection_proxy._pool.dispose()
                raise exc.DisconnectionError() from err
            else:
                raise

    logger.debug('Point (__init__) #5')

    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    logger.debug('Point (__init__) #6')
    return app
