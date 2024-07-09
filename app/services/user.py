from flask.sessions import SessionMixin
from app.models import User
from run import logger


logger.debug("userservice -> get_user_by_session")
def get_user_by_session(session: SessionMixin) -> User:
    return User.query.filter_by(steam64id=session['steam64id']).first()


logger.debug("userservice -> get_user_by_steam64id")
def get_user_by_steam64id(steam64id: int) -> User:

    steam64id = int(steam64id)

    return User.query.filter_by(steam64id=steam64id).first()


logger.debug("userservice -> user_exists")
def user_exists(steam64id: int) -> bool:

    steam64id = int(steam64id)

    user_existence = User.query.filter_by(steam64id=steam64id).first()
    return user_existence is not None