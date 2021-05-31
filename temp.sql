-- SQLite
SELECT
    sum(
        case
            when trans = "BUY" then qty
            when trans = "SELL" then -qty
        end
    ) as shares
from stocks
where
    owner = 'pacifistbunny#9855'
    and symbol = 'AAPL'
