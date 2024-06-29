from app.models import User, db


def user_exists(steam64id: int) -> bool:
    user_existence = User.query.filter_by(steam64id=steam64id).first()
    return user_existence is not None


def add_cart_notification(steam64id: int, amount: int) -> None:
    if not user_exists(steam64id):
        raise Exception("Steam ID not found")

    user: User = User.query.filter_by(steam64id=steam64id).first()

    user.cart_notifications += amount
    db.session.add(user)
    db.session.commit()


def remove_cart_notification(steam64id: int, amount: int) -> None:
    if not user_exists(steam64id):
        raise Exception("Steam ID not found")

    user: User = User.query.filter_by(steam64id=steam64id).first()

    user.cart_notifications -= amount
    db.session.add(user)
    db.session.commit()


def empty_cart_notification(steam64id: int) -> None:
    if not user_exists(steam64id):
        raise Exception("Steam ID not found")

    user: User = User.query.filter_by(steam64id=steam64id).first()
    user.cart_notifications = 0
    db.session.add(user)
    db.session.commit()



