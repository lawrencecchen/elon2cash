CREATE TABLE [IF NOT EXISTS] stocks (

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    owner text,
    trans text,
    symbol text,
    qty real,
    price real
)
