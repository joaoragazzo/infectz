from app.models import db, Cart, Item
from app.exceptions.itemDontExistsException import ItemDontExistsException
from app.services.item import item_exists



def add_cart_item(user_id: int, item_id: int) -> None:
    if not item_exists(item_id):
        raise ItemDontExistsException("This item does not exists in our database.")

    try:
        db.session.add(Cart(item_id=item_id, user_id=user_id))
        db.session.commit()
    except Exception as e:
        raise e


def remove_cart_item(user_id: int, item_id: int) -> None:
    if not item_exists(item_id):
        raise Exception("This item does not exists in our database.")

    item_to_remove = Item.query.filter_by(item_id=item_id, user_id=user_id).first()

    try:
        db.session.remove(Cart(item_to_remove))
        db.session.commit()
    except Exception as e:
        raise e

