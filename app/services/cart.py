from app.models import db, Cart
from app.exceptions.itemDontExistsException import ItemDontExistsException
from app.services.item import item_exists
from app.exceptions.cartItemDontExistsException import cartItemDontExistsException

def add_cart_item(user_id: int, item_id: int) -> None:
    if not item_exists(item_id):
        raise ItemDontExistsException("This item does not exists in our database.")

    db.session.add(Cart(item_id=item_id, user_id=user_id))
    db.session.commit()


def remove_cart_item(user_id: int, item_id: int) -> None:
    if not item_exists(item_id):
        raise ItemDontExistsException("This item does not exists in our database.")

    cart_item_to_remove = Cart.query.filter_by(item_id=item_id, user_id=user_id).first()

    if cart_item_to_remove is None:
        raise cartItemDontExistsException("This cart item does not exists in our database.")


    db.session.delete(cart_item_to_remove)
    db.session.commit()

