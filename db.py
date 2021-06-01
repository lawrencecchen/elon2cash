# from bot import to_upper
import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    """
    create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn


con = create_connection("./database.db")


def init_tables():
    c = con.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS stocks (
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            owner text,
            trans text,
            symbol text,
            qty real,
            price real
        );
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS balances (
            owner text PRIMARY KEY,
            balance real DEFAULT 10000
        )
        """
    )
    c.execute(
        """
        CREATE TRIGGER IF NOT EXISTS create_balance_new_user
            BEFORE INSERT on stocks
        BEGIN
            INSERT OR IGNORE INTO balances (owner) VALUES (NEW.owner);
        END;
        """
    )

    # c.execute("""
    #   create trigger if not exists qty_cannot_be_negative_check
    #         after insert on stocks
    #     begin
    #         select
    #             case
    #                 when (
    #                     select
    #                         sum(
    #                             case
    #                                 when trans = "BUY" then qty
    #                                 when trans = "SELL" then -qty
    #                             end
    #                         )
    #                         from stocks
    #                         where
    #                             owner = NEW.owner
    #                             and symbol = NEW.symbol
    #                 ) + NEW.qty < 0 THEN
    #                     RAISE (ABORT, "You suck!")
    #                 END;
    #             END;
    # """)
    con.commit()


def get_balance(owner):
    c = con.cursor()
    c.row_factory = sqlite3.Row
    row = c.execute(
        """
        SELECT * FROM balances WHERE owner = ?
    """,
        [str(owner)],
    ).fetchone()
    con.commit()
    return dict(row)


def buy(owner: str, symbol: str, qty: float, price: float):
    c = con.cursor()
    c.execute(
        """
        UPDATE balances SET balance = balance - ? WHERE owner = ?
        """,
        [float(price), str(owner)],
    )
    c.execute(
        """
        INSERT INTO stocks
            (owner, trans, symbol, qty, price)
        VALUES
            (?, 'BUY', ?, ?, ?)
        """,
        [str(owner), str(symbol), float(qty), float(price)],
    )
    con.commit()


def get_current_holdings(owner, symbol):
    c = con.cursor()
    c.row_factory = sqlite3.Row
    row = c.execute(
        """
        SELECT
            sum(
                case
                    when trans = "BUY" then qty
                    when trans = "SELL" then -qty
                end
            ) as qty
        from stocks
        where
            owner = ?
            and symbol = ?
    """,
        [str(owner), str(symbol)],
    ).fetchone()
    con.commit()

    return dict(row)


def sell(owner, symbol, qty, price):
    c = con.cursor()
    c.row_factory = sqlite3.Row
    c.execute(
        """
        INSERT INTO stocks
            (owner, trans, symbol, qty, price)
        VALUES
            (?, 'SELL', ?, ?, ?)
        """,
        [str(owner), str(symbol), float(qty), float(price)],
    )
    con.commit()


def get_portfolio(owner):
    c = con.cursor()
    c.row_factory = sqlite3.Row
    rows = c.execute(
        """
        SELECT
            symbol, sum(
                case
                    when trans = "BUY" then qty
                    when trans = "SELL" then -qty
                end
            ) as shares
        from stocks
        where
            owner = ?
        group by symbol;
    """,
        [str(owner)],
    ).fetchall()
    con.commit()

    return [dict(ix) for ix in rows]
    # return json.dumps([dict(ix) for ix in rows])
