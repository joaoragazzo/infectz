from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.pool import Pool

db: SQLAlchemy = SQLAlchemy()


def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')

    app.config.from_object('app.config.Config')
    db.init_app(app)

    @event.listens_for(Pool, "connect")
    def connect(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("SET SESSION wait_timeout = 28800")
        cursor.close()

    @event.listens_for(Pool, "checkout")
    def checkout(dbapi_connection, connection_record, connection_proxy):
        try:
            dbapi_connection.cursor().execute("SELECT 1")
        except Exception as exc:
            raise exc

    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
