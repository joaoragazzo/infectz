from flask.sessions import SessionMixin
from app.models import db, Cart
from app.exceptions.itemDontExistsException import ItemDontExistsException
from app.services.item import item_exists
from app.exceptions.cartItemDontExistsException import cartItemDontExistsException


def get_all_cart_items(session: SessionMixin) -> Cart:
    return Cart.query.filter_by(user_id=session['steam64id']).all()


def add_cart_item(session: SessionMixin, item_id: int) -> None:
    if not item_exists(item_id):
        raise ItemDontExistsException("This item does not exists in our database.")

    db.session.add(Cart(item_id=item_id, user_id=session['steam64id']))
    db.session.commit()


def remove_cart_item(session: SessionMixin, item_id: int) -> None:
    if not item_exists(item_id):
        raise ItemDontExistsException("This item does not exists in our database.")

    cart_item_to_remove = Cart.query.filter_by(item_id=item_id, user_id=session['steam64id']).first()

    if cart_item_to_remove is None:
        raise cartItemDontExistsException("This cart item does not exists in our database.")


    db.session.delete(cart_item_to_remove)
    db.session.commit()

