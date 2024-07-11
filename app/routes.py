from run import logger

from flask import render_template, request, redirect, session, Blueprint, jsonify
from app.config import Config
from app.models import db, Item, User, Inventory, Category, Cart, Payment
from app.middleware import login_required

from app.enums.notificationsTypes import NotificationsTypes
from app.exceptions.itemDontExistsException import ItemDontExistsException
from app.exceptions.cartItemDontExistsException import cartItemDontExistsException
from app.exceptions.emptyCartException import EmptyCartException
from app.exceptions.invalidCPF import InvalidCPF

from app.services.discord import send_webhook_discord_message
from mercadopago import SDK
from collections import defaultdict

import app.services.notifications as notification_service
import app.services.cart as cart_service
import app.services.user as user_service
import app.services.inventory as inventory_service
import app.services.utils as utils_service
import app.services.mercadopago as mercadopago_service
import app.services.payment as payment_service

import markupsafe
import requests
import datetime
from urllib.parse import urlencode


main = Blueprint('main', __name__)

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
        steam64id = request.args.get('openid.claimed_id').split('/')[-1]

        url = 'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/'
        params = {
            'key': Config.STEAM_API_KEY,
            'steamids': steam64id
        }

        response = requests.get(url, params=params)
        data = response.json()

        if 'response' in data and 'players' in data['response'] and len(data['response']['players']) > 0:
            player_data = data['response']['players'][0]

            session['name'] = markupsafe.escape(player_data.get('personaname'))
            session['avatar'] = player_data.get('avatarfull')
            session['steam64id'] = steam64id
            session['notifications'] = []

            now = datetime.datetime.now()

            if not user_service.user_exists(int(steam64id)):
                user = User(
                    steam64id=steam64id,
                    first_login=now,
                    last_login=now
                )
            else:
                user: User = user_service.get_user_by_steam64id(int(steam64id))
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
    if data['action'] == 'payment.updated':
        mercadopago_id = data['data']['id']
        user = payment_service.check_payment_owner(mercadopago_id)
        payments_number = payment_service.check_payment_amount(mercadopago_id)

        approved = mercadopago_service.check_approved_payment(mercadopago_id)

        if approved:
            payment_service.approve_payment(mercadopago_id)
            inventory_service.move_from_payment_to_inventory(mercadopago_id)
            notification_service.add_inventory_notification(user.steam64id, payments_number)
        else:
            payment_service.expire_payment(mercadopago_id)

    send_webhook_discord_message(str(data))
    return jsonify({"status": "success"}), 200


@main.route('/')
def main_page():
    user: User = None
    notifications = []
    if session.get('steam64id') is not None:
        user: User = user_service.get_user_by_session(session)
        notifications = notification_service.get_temporary_notifications(session)

    return render_template('main.html',
                           user=user,
                           notifications=notifications
                           )


@main.route('/cart', methods=['GET'])
@login_required
def cart():
    user: User = user_service.get_user_by_session(session)

    cart_items: list[Cart] = cart_service.get_all_cart_items(session)

    notification_service.empty_cart_notification(session)

    cart_items_dict = defaultdict(lambda: {'count': 0, 'price': 0, 'image': '', 'id': 0})

    for cart_item in cart_items:
        item_name = cart_item.item.name
        cart_items_dict[item_name]['id'] = cart_item.item.id
        cart_items_dict[item_name]['name'] = item_name
        cart_items_dict[item_name]['count'] += 1
        cart_items_dict[item_name]['price'] = f"{cart_item.item.price:.2f}"
        cart_items_dict[item_name]['image'] = cart_item.item.image_url

    cart_items_final: list[dict] = list(cart_items_dict.values())

    return render_template('logged/cart.html',
                           user=user,
                           cart_items=cart_items_final
                           )


@main.route('/cart', methods=['POST'])
@login_required
def cart_add_item():
    item_id: int = int(request.form.get('item_id'))
    action: str = request.form.get('action')

    try:
        if action == 'add':
            cart_service.add_cart_item(session, item_id)
            notification_service.add_cart_notification(session, 1)
            message: str = "Item adicionado com sucesso!"
            status: str = "success"
        elif action == 'remove':
            cart_service.remove_cart_item(session, item_id)
            notification_service.remove_cart_notification(session, 1)
            message: str = "Item removido com sucesso!"
            status: str = "success"
        else:
            return jsonify({"status": "error", 'message': 'Item ou ação desconhecidos'}), 400

    except (ItemDontExistsException, cartItemDontExistsException):
        return jsonify({'status': 'error', 'message': 'Item ou ação desconhecidos'}), 400

    return jsonify({'status': status, 'message': message}), 200


@main.route('/shop')
@login_required
def shop():
    store = Category.query.all()
    user: User = user_service.get_user_by_session(session)

    return render_template('loja/store.html',
                           user=user,
                           store=store
                           )


@main.route('/inventory')
@login_required
def inventory():
    user: User = user_service.get_user_by_session(session)
    inventory: list[Inventory] = inventory_service.get_inventory(session)

    return render_template('logged/inventory.html',
                           user=user,
                           inventory=(inventory if inventory is not None else []),
                           )


@main.route('/account')
@login_required
def account():
    user: User = user_service.get_user_by_session(session)

    return render_template('logged/config.html',
                           user=user)


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
                      price=1.0, price_off=0, image_url='/static/img/itens/mosin.jpg')
    db.session.add(mosin_item)
    db.session.commit()

    m4a1_item = Item(category_id=1, name="M4A1", description="Arma média",
                     price=2.0, price_off=0, image_url='/static/img/itens/m4a1.jpg')
    db.session.add(m4a1_item)
    db.session.commit()

    armalite = Item(category_id=1, name="ArmaLite", description="Arma boa",
                    price=99.0, price_off=0, image_url='/static/img/itens/armalite.jpeg')
    db.session.add(armalite)
    db.session.commit()

    mi17 = Item(category_id=2, name="MI17", description="Veiculo que o alemao fica brabo",
                price=1.0, price_off=0, image_url='/static/img/itens/mi17.jpg')
    db.session.add(mi17)
    db.session.commit()

    return redirect('/')


@main.route('/pay')
@login_required
def pay():
    user: User = user_service.get_user_by_session(session)
    notification_service.empty_cart_notification(session)

    cart_items: list[Cart] = cart_service.get_all_cart_items(session)

    if not cart_items:
        notification_service.send_notification(session, NotificationsTypes.ERROR.value, "Seu carrinho está vazio. Impossível de prosseguir.")
        return redirect('/')

    cart_items_dict = defaultdict(lambda: {'count': 0, 'price': 0, 'image': '', 'id': 0, 'total_price': 0})

    total_price = 0

    for cart_item in cart_items:
        total_price += cart_item.item.price
        item_name = cart_item.item.name
        cart_items_dict[item_name]['id'] = cart_item.item.id
        cart_items_dict[item_name]['name'] = item_name
        cart_items_dict[item_name]['count'] += 1
        cart_items_dict[item_name]['price'] = f"{cart_item.item.price:.2f}"
        cart_items_dict[item_name]['total_price'] = f"{(float(cart_items_dict[item_name]['total_price']) + cart_item.item.price):.2f}"
        cart_items_dict[item_name]['image'] = cart_item.item.image_url

    cart_items_final: list[dict] = list(cart_items_dict.values())

    total_price = f"{total_price:.2f}"

    return render_template('loja/pay.html',
                           user=user,
                           cart_items=cart_items_final,
                           total_price=total_price
                           )


@main.route('/pay/details')
@login_required
def pay_details():
    user: User = user_service.get_user_by_session(session)
    notification_service.empty_cart_notification(session)

    cart_items: list[Item] = cart_service.get_all_cart_items(session)

    if not cart_items:
        notification_service.send_notification(session, NotificationsTypes.ERROR.value, "Seu carrinho está vazio. Impossível de prosseguir.")
        return redirect('/')

    return render_template('loja/collect-informations.html', user=user)


@main.route('/pay/checkout', methods=['POST'])
@login_required
def pay_checkout():
    user: User = user_service.get_user_by_session(session)
    notification_service.empty_cart_notification(session)

    cart_items: list[Item] = cart_service.get_all_cart_items(session)

    try:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        cpf = request.form['cpf']
        email = request.form['email']
    except KeyError:
        notification_service.send_notification(session, NotificationsTypes.ERROR.value,
                          "As informações não foram preenchidas corretamente. Impossível prosseguir.")
        return redirect('/')

    cpf = cpf.replace("-", "").replace(".", '')

    try:
        utils_service.is_valid_data(cart_items, cpf)
    except (EmptyCartException, InvalidCPF) as e:
        notification_service.send_notification(session, NotificationsTypes.ERROR.value, e.msg)

    total_value = 0
    for item in cart_items:
        total_value += item.item.price

    payment_id, qr_code_base64, qr_code = mercadopago_service.create_payment(total_value, email, first_name, last_name, cpf)
    payment_service.create_payment(user, payment_id)

    return render_template('loja/pix.html',
                           base64qrcode=qr_code_base64,
                           qr_code_min=qr_code[:35],
                           qr_code=qr_code,
                           user=user
                           )
