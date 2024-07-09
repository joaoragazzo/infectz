from run import logger
from app.models import User, db
from app.exceptions.userDontExitsException import UserDontExistsException
from app.services.user import user_exists
from flask.sessions import SessionMixin


logger.debug("notification -> add_cart_notification")
def add_cart_notification(session: SessionMixin, amount: int) -> None:
    if not user_exists(session['steam64id']):
        raise UserDontExistsException("Steam ID not found")

    user: User = User.query.filter_by(steam64id=session['steam64id']).first()

    user.cart_notifications += amount
    db.session.add(user)
    db.session.commit()

logger.debug("notification -> remove_cart_notification")
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


logger.debug("notification -> send_notification")
def send_notification(session: SessionMixin, notification_type: str, content: str) -> None:
    if 'notifications' not in session:
        session['notifications'] = []

    session['notifications'] = [
        {
            'type': f'{notification_type}',
            'content': f'{content}'
        }
    ]


logger.debug("notification -> get_temporary_notifications")
def get_temporary_notifications(session: SessionMixin) -> list[dict]:
    try:
        if session.get('notifications') is not None:
            notifications = session['notifications'][:]
            session['notifications'] = []
            logger.debug(f"Returning notifications: {notifications}")
            return notifications
        logger.debug("No notifications found in session.")
        return []
    except Exception as e:
        logger.exception("An error occurred while getting temporary notifications." + e.__str__())
        return []

logger.debug("finished")