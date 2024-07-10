from . import db

class Clan(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tag = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    leader_id = db.Column(db.BigInteger, db.ForeignKey('user.steam64id'), nullable=True)

class User(db.Model):
    steam64id = db.Column(db.BigInteger, primary_key=True, unique=True, nullable=False)
    inventory_notifications = db.Column(db.Integer, nullable=True, default=0)
    shop_notifications = db.Column(db.Integer, nullable=True, default=0)
    config_notifications = db.Column(db.Integer, nullable=True, default=0)
    cart_notifications = db.Column(db.Integer, nullable=True, default=0)
    first_login = db.Column(db.DateTime, nullable=False)
    last_login = db.Column(db.DateTime, nullable=False)
    clan_id = db.Column(db.Integer, db.ForeignKey('clan.id'), nullable=True)
    role = db.Column(db.Enum('none', 'member', 'sub_leader', 'leader'), default='none', nullable=False)

    clan = db.relationship('Clan', backref='members', foreign_keys=[clan_id])
    inventory = db.relationship('Inventory', backref='user_inventory', lazy=True)
    cart = db.relationship('Cart', backref='user_cart', lazy=True)
    payments = db.relationship('Payment', backref='user_payments', lazy=True)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, default=True)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    price_off = db.Column(db.Float, default=0.0)
    image_url = db.Column(db.String(255), nullable=True)
    active = db.Column(db.Boolean, default=True)

    category = db.relationship('Category', backref='items', lazy=True)
    payments = db.relationship('Payment', backref='item_payments', lazy=True)
    inventory_items = db.relationship('Inventory', backref='item_inventory', lazy=True)
    cart_items = db.relationship('Cart', backref='item_cart', lazy=True)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    mercadopago_id = db.Column(db.BigInteger, nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.steam64id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    payment_confirmed = db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref='user_payments', lazy=True)
    item = db.relationship('Item', backref='item_payments', lazy=True)

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.steam64id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    redeemed = db.Column(db.Boolean, default=False)
    payment_id = db.Column(db.BigInteger, db.ForeignKey('payment.id'), nullable=False)

    user = db.relationship('User', backref='user_inventory', lazy=True)
    item = db.relationship('Item', backref='item_inventory', lazy=True)
    payment = db.relationship('Payment', backref='payment_inventory', lazy=True)

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.steam64id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)

    user = db.relationship('User', backref='user_cart', lazy=True)
    item = db.relationship('Item', backref='item_cart', lazy=True)
