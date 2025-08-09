-- #################################################################
-- # trade database
-- #################################################################
USE trade;

-- #################################################################
-- # 매수 후보 종목 테이블 (candidate_stock)
-- #################################################################

DROP TABLE IF EXISTS candidate_stock;

CREATE TABLE candidate_stock (
    id INT PRIMARY KEY AUTO_INCREMENT,
    corp_code VARCHAR(8),
    corp_name VARCHAR(150),
    stock_code VARCHAR(6),
    buy_price FLOAT,
    target_price FLOAT,
    stop_price FLOAT,
    date VARCHAR(10)
);

-- #################################################################
-- # 매수 정보 테이블 (purchase)
-- #################################################################

DROP TABLE IF EXISTS purchase;

CREATE TABLE purchase (
    id INT PRIMARY KEY AUTO_INCREMENT,
    buy_price FLOAT,
    target_price FLOAT,
    stop_price FLOAT
);
