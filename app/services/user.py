from app.models import User


def user_exists(steam64id: int) -> bool:
    user_existence = User.query.filter_by(steam64id=steam64id).first()
    return user_existence is not None