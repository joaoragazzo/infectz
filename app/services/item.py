from app.models import Item


def item_exists(item_id: int) -> bool:
    item_existence = Item.query.filter_by(id=item_id).first()
    return item_existence is not None