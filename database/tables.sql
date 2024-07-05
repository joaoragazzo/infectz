-- noinspection SqlNoDataSourceInspectionForFile
-- noinspection SqlDialectInspectionForFile

CREATE TABLE `user` (
    steam64id BIGINT(20) UNSIGNED PRIMARY KEY,
    inventory_notifications INT(11) DEFAULT 0,
    shop_notifications INT(11) DEFAULT 0,
    config_notifications INT(11) DEFAULT 0,
    cart_notifications INT(11) DEFAULT 0
);

CREATE TABLE `category` (
    id INT(11) AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    active BOOLEAN DEFAULT TRUE
);

CREATE TABLE `item` (
    id INT(11) AUTO_INCREMENT PRIMARY KEY,
    category_id INT(11) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    price FLOAT NOT NULL,
    price_off FLOAT DEFAULT 0.0,
    image_url VARCHAR(255) NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (category_id) REFERENCES `category`(id)
);

CREATE TABLE `inventory` (
    id INT(11) AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT(20) UNSIGNED NOT NULL,
    item_id INT(11) NOT NULL,
    redeemed BOOLEAN DEFAULT FALSE,
    date_bought DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES `user`(steam64id),
    FOREIGN KEY (item_id) REFERENCES `item`(id)
);

CREATE TABLE `cart` (
    id INT(11) AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT(20) UNSIGNED NOT NULL,
    item_id INT(11) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES `user`(steam64id),
    FOREIGN KEY (item_id) REFERENCES `item`(id)
);

CREATE TABLE `payment` (
    id INT(11) AUTO_INCREMENT PRIMARY KEY,
    mercado_pago_id INT(11) NOT NULL,
    user_id BIGINT(20) UNSIGNED NOT NULL,
    item_id INT(11) NOT NULL,
    created_at DATETIME NOT NULL,
    payment_confirmed BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES `user`(steam64id),
    FOREIGN KEY (item_id) REFERENCES `item`(id)
);