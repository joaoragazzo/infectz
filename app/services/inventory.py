from flask.sessions import SessionMixin
from app.models import Inventory
from app import db


def get_inventory(session: SessionMixin) -> list[Inventory]:
    return Inventory.query.filter_by(user_id=session['steam64id']).all()