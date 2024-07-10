from flask.sessions import SessionMixin
from app.models import Inventory, User, Payment
from app import db


def get_inventory(session: SessionMixin):
    return Inventory.query.filter_by(user_id=session['steam64id']).all()


def move_from_payment_to_inventory(mercadopago_id: int):
    payments = Payment.query.filter_by(mercado_pago_id=mercadopago_id).all()

    for payment in payments:
        new_inventory_item = Inventory(
            user_id=payment.user_id,
            item_id=payment.item_id,
            redeemed=False,
            payment_id=payment.id
        )
        db.session.add(new_inventory_item)

    db.session.commit()