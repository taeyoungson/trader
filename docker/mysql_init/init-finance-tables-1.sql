-- #################################################################
-- # finance database
-- #################################################################
USE finance;

-- #################################################################
-- # 기업 기본 정보 테이블 (corporate_info)
-- #################################################################

DROP TABLE IF EXISTS corporate_info;

CREATE TABLE corporate_info (
    corp_code VARCHAR(8) PRIMARY KEY,
    corp_name VARCHAR(150),
    corp_eng_name VARCHAR(150),
    stock_code VARCHAR(6),
    modify_date VARCHAR(8)
);

-- #################################################################
-- # 기업 시세 정보 테이블 (corporate_quote)
-- #################################################################

DROP TABLE IF EXISTS corporate_quote;

CREATE TABLE corporate_quote (
    symbol VARCHAR(6) PRIMARY KEY,
    market VARCHAR(10),
    sector_name VARCHAR(30),
    price FLOAT,
    volume BIGINT,
    amount BIGINT,
    market_cap BIGINT,
    sign VARCHAR(10),
    sign_name VARCHAR(20),
    risk VARCHAR(50),
    halt BOOLEAN,
    overbought VARCHAR(50),
    prev_price FLOAT,
    prev_volume BIGINT,
    `change` FLOAT, 
    rate FLOAT,
    high_limit FLOAT,
    low_limit FLOAT,
    unit INT,
    tick FLOAT,
    decimal_places INT,
    currency VARCHAR(10),
    exchange_rate FLOAT,
    open_price FLOAT,
    high_price FLOAT,
    low_price FLOAT,
    eps FLOAT,
    bps FLOAT,
    per FLOAT,
    pbr FLOAT,
    week52_high FLOAT,
    week52_low FLOAT,
    week52_high_date DATE,
    week52_low_date DATE
);
