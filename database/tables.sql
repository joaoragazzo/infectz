-- noinspection SqlNoDataSourceInspectionForFile
-- noinspection SqlDialectInspectionForFile

CREATE TABLE `clan` (
    id INT(11) AUTO_INCREMENT PRIMARY KEY,
    tag VARCHAR(10) NOT NULL,
    name VARCHAR(255) NOT NULL
  );

CREATE TABLE `user` (
    steam64id BIGINT(20) UNSIGNED PRIMARY KEY,
    inventory_notifications INT(11) DEFAULT 0,
    shop_notifications INT(11) DEFAULT 0,
    config_notifications INT(11) DEFAULT 0,
    cart_notifications INT(11) DEFAULT 0,
    first_login DATETIME NOT NULL,
    last_login DATETIME NOT NULL,
    clan_id INT(11),
    role ENUM('none', 'member', 'sub_leader', 'leader') DEFAULT 'none',
    FOREIGN KEY (clan_id) REFERENCES clan(id)
);

CREATE TABLE category (
    id INT(11) AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    active BOOLEAN DEFAULT TRUE
);

CREATE TABLE item (
    id INT(11) AUTO_INCREMENT PRIMARY KEY,
    category_id INT(11) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    price FLOAT NOT NULL,
    price_off FLOAT DEFAULT 0.0,
    image_url VARCHAR(255) NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (category_id) REFERENCES category(id)
);

CREATE TABLE payment (
    id INT(11) AUTO_INCREMENT PRIMARY KEY,
    mercadopago_id BIGINT(20) NOT NULL,
    user_id BIGINT(20) UNSIGNED NOT NULL,
    item_id INT(11) NOT NULL,
    created_at DATETIME NOT NULL,
    status ENUM('approved', 'pending', 'expired') DEFAULT 'pending' ,
    FOREIGN KEY (user_id) REFERENCES user(steam64id),
    FOREIGN KEY (item_id) REFERENCES item(id)
);

CREATE TABLE inventory (
    id INT(11) AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT(20) UNSIGNED NOT NULL,
    item_id INT(11) NOT NULL,
    redeemed BOOLEAN DEFAULT FALSE,
    payment_id INT(11) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(steam64id),
    FOREIGN KEY (item_id) REFERENCES item(id),
    FOREIGN KEY (payment_id) REFERENCES payment(id)
);

CREATE TABLE cart (
    id INT(11) AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT(20) UNSIGNED NOT NULL,
    item_id INT(11) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(steam64id),
    FOREIGN KEY (item_id) REFERENCES item(id)
);
