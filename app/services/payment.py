from app.models import db, User, Cart, Payment
import datetime
from run import logger


def create_payment(user: User, mercadopago_id: int):
    """
    Change every item on Cart to Payment table

    :param user:
    :param mercadopago_id:
    :return:
    """
    now = datetime.datetime.now()

    cart_items = Cart.query.filter_by(user_id=user.steam64id).all()

    for cart_item in cart_items:
        new_payment = Payment(
            user_id=user.steam64id,
            mercadopago_id=mercadopago_id,
            item_id=cart_item.item.id,
            created_at=now
        )
        db.session.add(new_payment)
        db.session.delete(cart_item)

    db.session.commit()


def approve_payment(mercadopago_id: int):
    logger.debug("approve_payment.payment.mercado_pago.id: " + str(mercadopago_id))
    """
    Approve all payments in payment table

    :param mercadopago_id:
    :return:
    """

    purchases = Payment.query.filter_by(mercadopago_id=mercadopago_id).all()

    for purchase in purchases:
        logger.debug("foi um, e outro?")
        purchase.approved = True
        db.session.add(purchase)

    db.session.commit()