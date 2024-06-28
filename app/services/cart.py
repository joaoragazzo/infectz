# from app.models import db, Cart, Item
#
#
# def check_item_existence(item_id: int) -> bool:
#     item_existence = Item.query.filter_by(id=item_id).query().first()
#     return item_existence
#
#
# def add_cart_item(item_id: int, user_id: int) -> None:
#     if not check_item_existence(item_id):
#         pass
#
#     try:
#         db.session.add(Cart(item_id, user_id))
#         db.session.commit()
#     except Exception as e:
#         raise e
#
#
# def remove_cart_item(item_id: int, user_id: int) -> None:
#     if not check_item_existence(item_id):
#         pass
#
#     item_to_remove = Item.query.filter_by(item_id=item_id, user_id=user_id).first()
#
#     try:
#         db.session.remove(Cart(item_to_remove))
#         db.session.commit()
#     except Exception as e:
#         raise e
