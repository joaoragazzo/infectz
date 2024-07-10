import mercadopago
from app.config import Config
from run import logger

mercadopago_sdk = mercadopago.SDK(Config.MERCADO_PAGO_SDK_KEY)


def create_payment(total_value: int, email: str, first_name: str, last_name: str, cpf_number: str):
    """
    Create a payment request for a purchase on MercadoPago API

    :param cpf_number:
    :param total_value:
    :param email:
    :param first_name:
    :param last_name:
    :return: The payment id, QR Code Base64, QRCode
    """

    payment_data = {
        "transaction_amount": total_value,
        "description": "Doação",
        "payment_method_id": "pix",
        "payer": {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "identification": {
                "type": "cpf",
                "number": cpf_number
            }
        }
    }

    payment_response = mercadopago_sdk.payment().create(payment_data)
    logger.debug("CRIANDO A SOLICITAÇÃO DE PAGAMENTO:" + str(payment_response))
    return (payment_response['response']['id'],
            payment_response['response']['point_of_interaction']['transaction_data']['qr_code_base64'],
            payment_response['response']['point_of_interaction']['transaction_data']['qr_code'])


def check_approved_payment(payment_id: int):
    """
    Verify the payment is approved

    :param payment_id:
    :return: Boolean state of the payment
    """

    payment_response = mercadopago_sdk.payment().search({'id': payment_id})
    logger.debug(f"CHECANDO STATUS DO ID {payment_id}:" + str(payment_response))
    logger.debug(f">>> {payment_response['response']['results'][0]['status']}")
    return payment_response['response']['results'][0]['status'] == 'approved'
