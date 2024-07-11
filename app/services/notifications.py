from run import logger
from app.models import User, db
from app.exceptions.userDontExitsException import UserDontExistsException
from app.services.user import user_exists
from flask.sessions import SessionMixin


def add_cart_notification(session: SessionMixin, amount: int) -> None:
    if not user_exists(session['steam64id']):
        raise UserDontExistsException("Steam ID not found")

    user: User = User.query.filter_by(steam64id=session['steam64id']).first()

    user.cart_notifications += amount
    db.session.add(user)
    db.session.commit()


def add_inventory_notification(session: SessionMixin, amount: int) -> None:
    if not user_exists(session['steam64id']):
        raise UserDontExistsException("Steam ID not found")

    user: User = User.query.filter_by(steam64id=session['steam64id']).first()

    user.inventory_notifications += amount
    db.session.add(user)
    db.session.commit()


def add_inventory_notification_by_steam64id(steam64id: int, amount: int) -> None:
    if not user_exists(steam64id):
        raise UserDontExistsException("Steam ID not found")

    user: User = User.query.filter_by(steam64id=steam64id).first()

    user.inventory_notifications += amount
    db.session.add(user)
    db.session.commit()

def remove_cart_notification(session: SessionMixin, amount: int) -> None:
    if not user_exists(session['steam64id']):
        raise UserDontExistsException("Steam ID not found")

    user: User = User.query.filter_by(steam64id=session['steam64id']).first()

    if user.cart_notifications > 0:
        user.cart_notifications -= amount
        db.session.add(user)
        db.session.commit()


def empty_cart_notification(session: SessionMixin) -> None:
    if not user_exists(session['steam64id']):
        raise UserDontExistsException("Steam ID not found")

    user: User = User.query.filter_by(steam64id=session['steam64id']).first()
    user.cart_notifications = 0
    db.session.add(user)
    db.session.commit()


def send_notification(session: SessionMixin, notification_type: str, content: str) -> None:
    if 'notifications' not in session:
        session['notifications'] = []

    session['notifications'] = [
        {
            'type': f'{notification_type}',
            'content': f'{content}'
        }
    ]


def get_temporary_notifications(session: SessionMixin):
    if session.get('notifications') is not None:
        notifications = session['notifications'][:]
        session['notifications'] = []
        return notifications
    return []

