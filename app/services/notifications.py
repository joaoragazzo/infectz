from run import logger

logger.debug("Fazendo os imports das bibliotecas do notification service")
logger.debug("Import #1")
from app.models import User, db
logger.debug("Import #2")
from app.exceptions.userDontExitsException import UserDontExistsException
logger.debug("Import #3")
from app.services.user import user_exists
logger.debug("Import #4")
from flask.sessions import SessionMixin
logger.debug("Feito com sucesso!")


def add_cart_notification(session: SessionMixin, amount: int) -> None:
    if not user_exists(session['steam64id']):
        raise UserDontExistsException("Steam ID not found")

    user: User = User.query.filter_by(steam64id=session['steam64id']).first()

    user.cart_notifications += amount
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


def send_notification(session: SessionMixin, type: str, content: str) -> None:
    if 'notifications' not in session:
        session['notifications'] = []

    session['notifications'] = [
        {
            'type': f'{type}',
            'content': f'{content}'
        }
    ]


def get_temporary_notifications(session: SessionMixin) -> list[dict]:
    if session.get('notifications') is not None:
        notifications = session['notifications'].copy()
        session['notifications'] = []
        return notifications
    return []
