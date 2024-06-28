from . import db


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    price_off = db.Column(db.Float, nullable=True, default=0.0)

    category = db.relationship('Category', backref='items', lazy=True)


class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.steam64id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    redeemed = db.Column(db.Boolean, nullable=False, default=False)
    date_bought = db.Column(db.DateTime, nullable=False)

    item = db.relationship('Item', backref='inventory_items', lazy=True)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)


class User(db.Model):
    steam64id = db.Column(db.BigInteger, primary_key=True, unique=True, nullable=False)
    inventory_notifications = db.Column(db.Integer, nullable=True, default=0)
    shop_notifications = db.Column(db.Integer, nullable=True, default=0)
    config_notifications = db.Column(db.Integer, nullable=True, default=0)
    cart_notifications = db.Column(db.Integer, nullable=True, default=0)

    inventory = db.relationship('Inventory', backref='user', lazy=True)
    cart = db.relationship('Cart', backref='user', lazy=True)


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.steam64id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)


    item = db.relationship('Item', backref='cart_items', lazy=True)
