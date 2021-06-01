import alpaca_trade_api as trade_api
from dotenv import load_dotenv
import os
from discord.ext import commands
import db

# initialize database
load_dotenv()
db.init_tables()

ALPACA_API_KEY = os.environ.get("ALPACA_API_KEY")
ALPACA_API_SECRET = os.environ.get("ALPACA_API_SECRET")
APCA_API_BASE_URL = os.environ.get("APCA_API_BASE_URL")
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")

api = trade_api.REST(ALPACA_API_KEY, ALPACA_API_SECRET, APCA_API_BASE_URL, "v2")


def current_price(stock: str) -> float:
    real_stock = stock.upper()
    barset = api.get_barset(real_stock, "1Min", limit=1)
    bars = barset[real_stock]
    current_price = bars[-1].c

    return float(current_price)


bot = commands.Bot(command_prefix="!")


def to_upper(argument):
    return argument.upper()


@bot.command()
async def clock(ctx):
    clock = api.get_clock()
    await ctx.send("The market is {}".format("open." if clock.is_open else "closed."))


@bot.command()
async def price(ctx, symbol: to_upper):
    try:
        await ctx.send(
            "{} is currently trading at ${:,.2f}".format(symbol, current_price(symbol))
        )
    except:
        await ctx.send("{} is not a valid stock.".format(symbol))


@bot.command()
async def avg(ctx, symbol: to_upper):
    try:
        barset = api.get_barset(symbol, "day", limit=5)
        bars = barset[symbol]
        week_open = bars[0].o
        week_close = bars[-1].c
        percent_change = (week_close - week_open) / week_open * 100
        await ctx.send(
            "{} moved {}% over the last 5 days".format(symbol, percent_change)
        )
    except:
        await ctx.send("{} is not a valid stock.".format(symbol))


@bot.command()
async def p(ctx):
    try:

        def _format_stock(stock):
            symbol = stock["symbol"]
            shares = stock["shares"]
            total_value = float(current_price(symbol)) * shares
            result = """{}: {:,.2f} shares (currently ${:,.2f})\n""".format(
                symbol, shares, total_value
            )
            return result

        portfolio = db.get_portfolio(ctx.author)
        if len(portfolio) == 0:
            return await ctx.channel.send(
                "Your portfolio is empty, {}".format(str(ctx.author))
            )
        result = "".join(map(_format_stock, portfolio))
        await ctx.channel.send("""{}'s Portfolio: \n{}""".format(ctx.author, result))
    except Exception as e:
        print(e)
        await ctx.channel.send(
            "{}'s portfolio could not be found.", format(str(ctx.author))
        )


@bot.command()
async def buy(ctx, symbol: to_upper, price: float):
    try:
        shares = price / current_price(symbol)
        db.buy(ctx.author, symbol, shares, price)
        await ctx.channel.send(
            "{} bought {:,.2f} shares of {} for ${:,.2f}.".format(
                str(ctx.author), shares, symbol, price
            )
        )
    except Exception as e:
        print(e)
        await ctx.channel.send("Could not buy for {}.".format(str(ctx.author)))


@bot.command()
async def sell(ctx, symbol: to_upper, price: float):
    try:
        shares = float(price) / current_price(symbol)
        current = db.get_current_holdings(ctx.author, symbol)
        if current["qty"] - shares < 0:
            return await ctx.channel.send("Not enough shares to sell.")
        db.sell(ctx.author, symbol, shares, price)
        await ctx.channel.send(
            "{} sold ${:,.2f} of {}.".format(str(ctx.author), float(price), symbol)
        )
    except Exception as e:
        print(e)
        await ctx.channel.send("Could not sell for {}.".format(str(ctx.author)))


@bot.command()
async def my(ctx, symbol: to_upper):
    try:
        current = db.get_current_holdings(ctx.author, symbol)
        await ctx.channel.send(
            """{}'s owns {} shares of {}""".format(ctx.author, current["qty"], symbol)
        )
    except Exception as e:
        print(e)
        await ctx.channel.send("You don't own this stock, {}.".format(str(ctx.author)))


@bot.command()
async def balance(ctx):
    try:
        balance = db.get_balance(ctx.author)
        print(balance)
        await ctx.channel.send(
            "{}'s balance is: ${:,.2f}".format(
                str(ctx.author), float(balance["balance"])
            )
        )
    except Exception as e:
        print(e)
        await ctx.channel.send(
            "Could not fetch balance for {}.".format(str(ctx.author))
        )


bot.run(DISCORD_TOKEN)
