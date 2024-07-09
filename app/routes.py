from flask import render_template, request, redirect, session, Blueprint, flash, jsonify
from app.config import Config
from app.models import db, Item, User, Inventory, Category, Cart, Payment
from app.middleware import login_required
from app.services.cart import add_cart_item, remove_cart_item
from app.services.notifications import add_cart_notification, remove_cart_notification, empty_cart_notification, send_notification
from app.enums.notificationsTypes import NotificationsTypes
from app.exceptions.itemDontExistsException import ItemDontExistsException
from app.exceptions.cartItemDontExistsException import cartItemDontExistsException
from app.services.discord import send_webhook_discord_message
from app.services.utils import is_valid_cpf
from mercadopago import SDK
from collections import defaultdict
import markupsafe
import requests
import datetime
from urllib.parse import urlencode

main = Blueprint('main', __name__)

mercadopago_sdk = SDK(Config.MERCADO_PAGO_SDK_KEY)

@main.route('/login')
def login():
    params = {
        'openid.ns': 'http://specs.openid.net/auth/2.0',
        'openid.mode': 'checkid_setup',
        'openid.return_to': f'{Config.SERVER_SITE_URL}/authorize',
        'openid.realm': f'{Config.SERVER_SITE_URL}',
        'openid.identity': 'http://specs.openid.net/auth/2.0/identifier_select',
        'openid.claimed_id': 'http://specs.openid.net/auth/2.0/identifier_select'
    }
    query_string = urlencode(params)
    auth_url = f'https://steamcommunity.com/openid/login?{query_string}'
    return redirect(auth_url)


@main.route('/authorize')
def authorize():
    params = {
        'openid.assoc_handle': request.args.get('openid.assoc_handle'),
        'openid.signed': request.args.get('openid.signed'),
        'openid.sig': request.args.get('openid.sig'),
        'openid.ns': request.args.get('openid.ns'),
        'openid.mode': 'check_authentication',
        'openid.op_endpoint': request.args.get('openid.op_endpoint'),
        'openid.claimed_id': request.args.get('openid.claimed_id'),
        'openid.identity': request.args.get('openid.identity'),
        'openid.return_to': request.args.get('openid.return_to'),
        'openid.response_nonce': request.args.get('openid.response_nonce'),
    }

    response = requests.post('https://steamcommunity.com/openid/login', data=params)
    if 'is_valid:true' in response.text:
        steam_id = request.args.get('openid.claimed_id').split('/')[-1]

        url = 'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/'
        params = {
            'key': Config.STEAM_API_KEY,
            'steamids': steam_id
        }

        response = requests.get(url, params=params)
        data = response.json()

        if 'response' in data and 'players' in data['response'] and len(data['response']['players']) > 0:
            player_data = data['response']['players'][0]

            session['name'] = markupsafe.escape(player_data.get('personaname'))
            session['avatar'] = player_data.get('avatarfull')
            session['steam64id'] = steam_id
            session['notifications'] = []

            now = datetime.datetime.now()

            if User.query.filter_by(steam64id=steam_id).first() is None:
                user = User(
                    steam64id=steam_id,
                    first_login=now,
                    last_login=now
                )
            else:
                user: User = User.query.filter_by(steam64id=steam_id).first()
                user.last_login = now

            db.session.add(user)
            db.session.commit()

        return redirect('/')
    else:
        return redirect('/')


@main.route('/logout')
def logout():
    session.clear()
    return redirect('/', 302)


@main.route('/mercadopago/payment-webhook', methods=['POST'])
def mercadopago_payment_webhook():
    data = request.get_json()
    send_webhook_discord_message(str(data))
    return jsonify({"status": "success"}), 200


@main.route('/')
def main_page():
    user: User = None
    notifications = []
    if session.get('steam64id') is not None:
        user = User.query.filter_by(steam64id=session['steam64id']).first()
        notifications = session['notifications'].copy()
        session['notifications'] = []

    return render_template('main.html',
                           user=user,
                           notifications=notifications
                           )


@main.route('/cart', methods=['GET'])
@login_required
def cart():
    user: User = User.query.filter_by(steam64id=session['steam64id']).first()
    empty_cart_notification(user.steam64id)

    cart_items: list[Item] = Cart.query.filter_by(user_id=user.steam64id).all()

    cart_items_dict = defaultdict(lambda: {'count': 0, 'price': 0, 'image': '', 'id': 0})

    for cart_item in cart_items:
        item_name = cart_item.item.name
        cart_items_dict[item_name]['id'] = cart_item.item.id
        cart_items_dict[item_name]['name'] = item_name
        cart_items_dict[item_name]['count'] += 1
        cart_items_dict[item_name]['price'] = cart_item.item.price
        cart_items_dict[item_name]['image'] = cart_item.item.image_url

    cart_items_final: list[dict] = list(cart_items_dict.values())

    return render_template('logged/cart.html',
                           user=user,
                           cart_items=cart_items_final
                           )


@main.route('/cart', methods=['POST'])
@login_required
def cart_add_item():
    user: User = User.query.filter_by(steam64id=session['steam64id']).first()

    item_id: int = int(request.form.get('item_id'))
    action: str = request.form.get('action')

    status: str = "error"
    message: str = "Item ou ação desconhecidos!"

    try:
        if action == 'add':
            add_cart_item(user.steam64id, item_id)
            add_cart_notification(user.steam64id, 1)
            message: str = "Item adicionado com sucesso!"
            status: str = "success"

        elif action == 'remove':
            remove_cart_item(user.steam64id, item_id)
            remove_cart_notification(user.steam64id, 1)
            message: str = "Item removido com sucesso!"
            status: str = "success"
    except (ItemDontExistsException, cartItemDontExistsException):
        pass

    return jsonify({'status': status, 'message': message})


@main.route('/shop')
@login_required
def shop():
    store = Category.query.all()
    user = User.query.filter_by(steam64id=session['steam64id']).first()

    return render_template('loja/store.html',
                           user=user,
                           store=store
                           )


@main.route('/inventory')
@login_required
def inventory():
    inventory = Inventory.query.filter_by(user_id=session['steam64id']).all()
    user = User.query.filter_by(steam64id=session['steam64id']).first()
    return render_template('logged/inventory.html',
                           user=user,
                           inventory=(inventory if inventory is not None else []),
                           )


@main.route('/add-test-database')
def add_itens():
    guns_category = Category(name="Armas")  # ID: 1
    db.session.add(guns_category)
    db.session.commit()

    vehicles_category = Category(name="Veículos")  # ID: 2
    db.session.add(vehicles_category)
    db.session.commit()

    bases_category = Category(name="Bases")  # ID: 3
    db.session.add(bases_category)
    db.session.commit()

    mosin_item = Item(category_id=1, name="Mosin", description="Arma ruim",
                      price=20.0, price_off=0, image_url='/static/img/itens/mosin.jpg')
    db.session.add(mosin_item)
    db.session.commit()

    m4a1_item = Item(category_id=1, name="M4A1", description="Arma média",
                     price=25.0, price_off=0, image_url='/static/img/itens/m4a1.jpg')
    db.session.add(m4a1_item)
    db.session.commit()

    armalite = Item(category_id=1, name="ArmaLite", description="Arma boa",
                    price=99.0, price_off=0, image_url='/static/img/itens/armalite.jpeg')
    db.session.add(armalite)
    db.session.commit()

    mi17 = Item(category_id=2, name="MI17", description="Veiculo que o alemao fica brabo",
                price=15.0, price_off=0, image_url='/static/img/itens/mi17.jpg')
    db.session.add(mi17)
    db.session.commit()

    return redirect('/')


@main.route('/pay')
@login_required
def pay():
    user: User = User.query.filter_by(steam64id=session['steam64id']).first()
    empty_cart_notification(user.steam64id)

    cart_items: list[Item] = Cart.query.filter_by(user_id=user.steam64id).all()

    if not cart_items:
        send_notification(session, NotificationsTypes.ERROR.value, "Seu carrinho está vazio. Impossível de prosseguir.")
        return redirect('/')

    cart_items_dict = defaultdict(lambda: {'count': 0, 'price': 0, 'image': '', 'id': 0})

    total_price = 0

    for cart_item in cart_items:
        total_price += cart_item.item.price
        item_name = cart_item.item.name
        cart_items_dict[item_name]['id'] = cart_item.item.id
        cart_items_dict[item_name]['name'] = item_name
        cart_items_dict[item_name]['count'] += 1
        cart_items_dict[item_name]['price'] = cart_item.item.price
        cart_items_dict[item_name]['image'] = cart_item.item.image_url

    cart_items_final: list[dict] = list(cart_items_dict.values())

    return render_template('loja/pay.html',
                           user=user,
                           cart_items=cart_items_final,
                           total_price=total_price
                           )


@main.route('/pay/details')
@login_required
def pay_details():
    user: User = User.query.filter_by(steam64id=session['steam64id']).first()
    empty_cart_notification(user.steam64id)

    cart_items: list[Item] = Cart.query.filter_by(user_id=user.steam64id).all()

    if not cart_items:
        send_notification(session, NotificationsTypes.ERROR.value, "Seu carrinho está vazio. Impossível de prosseguir.")
        return redirect('/')

    return render_template('loja/collect-informations.html', user=user)


@main.route('/pay/checkout', methods=['POST'])
@login_required
def pay_checkout():
    user: User = User.query.filter_by(steam64id=session['steam64id']).first()
    empty_cart_notification(user.steam64id)

    cart_items: list[Item] = Cart.query.filter_by(user_id=user.steam64id).all()

    try:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        cpf = request.form['cpf']
        email = request.form['email']

        zipcode = request.form['zip_code']
        federal_unity = request.form['federal_unit']
        city = request.form['city']
        neighborhood = request.form['neighborhood']
        street_name = request.form['street_name']
        street_number = request.form['street_number']
    except KeyError:
        send_notification(session, NotificationsTypes.ERROR.value,
                          "As informações não foram preenchidas corretamente. Impossível prosseguir.")
        return redirect('/')

    federal_units = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR",
                     "PE",
                     "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"]
    cpf = cpf.replace("-", "").replace(".", '')
    zipcode = zipcode.replace("-", "")

    if not cart_items:
        send_notification(session, NotificationsTypes.ERROR.value,
                          "Seu carrinho está vazio. Impossível de prosseguir.")
        return redirect('/')

    if not is_valid_cpf(cpf):
        send_notification(session, NotificationsTypes.ERROR.value,
                          "O CPF fornecido é inválido. Impossível prosseguir.")
        return redirect('/')

    if federal_unity not in federal_units:
        send_notification(session, NotificationsTypes.ERROR.value,
                          "O estado fornecido é inválido. Impossível prosseguir.")
        return redirect('/')

    if len(zipcode) != 8 or not zipcode.isdigit():
        send_notification(session, NotificationsTypes.ERROR.value,
                          "O CEP fornecido é inválido. Impossível prosseguir.")
        return redirect('/')

    total_value = 0
    for item in cart_items:
        total_value += item.item.price

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
                "number": cpf
            },
            "address": {
                "zip_code": zipcode,
                "street_name": street_name,
                "street_number": street_number,
                "neighborhood": neighborhood,
                "city": city,
                "federal_unit": federal_unity
            }
        }
    }

    payment_response = mercadopago_sdk.payment().create(payment_data)
    payment_id: int = payment_response['response']['id']
    now = datetime.datetime.now()

    for item in cart_items:
        payment: Payment = Payment(
            mercado_pago_id=payment_id,
            user_id=user.steam64id,
            item_id=item.item.id,
            created_at=now
        )
        db.session.add(payment)

    db.session.commit()


    base64qrcode = payment_response['response']['point_of_interaction']['transaction_data']['qr_code_base64']
    qr_code = payment_response['response']['point_of_interaction']['transaction_data']['qr_code']
    qr_code_min = qr_code[:27]

    return render_template('loja/pix.html',
                           base64qrcode=base64qrcode,
                           qr_code_min=qr_code_min,
                           qr_code=qr_code,
                           user=user
                           )



