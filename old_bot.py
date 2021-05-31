from logging import error
import discord
import alpaca_trade_api as trade_api
from dotenv import load_dotenv
import os
from discord.ext import commands
from db import init_db, buy, sell, get_portfolio,get_current_holdings


load_dotenv()
init_db()

ALPACA_API_KEY = os.environ.get('ALPACA_API_KEY')
ALPACA_API_SECRET = os.environ.get('ALPACA_API_SECRET')
APCA_API_BASE_URL = os.environ.get('APCA_API_BASE_URL')
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')


api = trade_api.REST(ALPACA_API_KEY, ALPACA_API_SECRET, APCA_API_BASE_URL, 'v2')

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

def current_price(stock: str)->float:
    real_stock = stock.upper()
    barset = api.get_barset(real_stock, '1Min', limit=1)
    bars = barset[real_stock]
    current_price = bars[-1].c

    return float(current_price)


portfolios = {}

# TODO revise bot to use commands: https://discordpy.readthedocs.io/en/stable/ext/commands/commands.html
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('~clock'):
        clock = api.get_clock()
        await message.channel.send('The market is {}'.format('open.' if clock.is_open else 'closed.'))

    if message.content.startswith('$'):
        symbol = message.content[1:].upper()
        try:
            await message.channel.send("{} is currently trading at ${:,.2f}".format(symbol, current_price(symbol)))
        except:
            await message.channel.send("{} is not a valid stock.".format(symbol))

    if message.content.startswith('!avg '):
        symbol = message.content[5:].upper()
        try:
            barset = api.get_barset(symbol, 'day', limit=5)
            bars = barset[symbol]
            week_open = bars[0].o
            week_close = bars[-1].c
            percent_change = (week_close - week_open) / week_open * 100
            await message.channel.send("{} moved {}% over the last 5 days".format(symbol, percent_change))
        except:
            await message.channel.send("{} is not a valid stock.".format(symbol))

    if message.content.startswith('!buy'):
        [_, symbol, price] = message.content.split(" ")
        try:
            shares = float(price) / current_price(symbol)
            buy(message.author, symbol.upper(), shares, price)
            await message.channel.send("{} bought {:,.2f} shares of {} for ${:,.2f}.".format(str(message.author), shares, symbol.upper(), float(price)))
        except:
            await message.channel.send("Could not buy for {}.".format(str(message.author)))

    if message.content.startswith('!sell'):
        [_, symbol, price] = message.content.split(" ")
        try:
            shares = float(price) / current_price(symbol)
            current = get_current_holdings(message.author, symbol.upper())
            if current["qty"] - shares < 0:
                return await message.channel.send("Not enough shares to sell.")
            sell(message.author, symbol.upper(), shares, price)
            await message.channel.send("{} sold ${:,.2f} of {}.".format(str(message.author), float(price), symbol.upper()))
        except:
            await message.channel.send("Could not sell for {}.".format(str(message.author)))

    if message.content.startswith('!my'):
        [_, symbol] = message.content.split(" ")
        try:
            current = get_current_holdings(message.author, symbol.upper())
            await message.channel.send(
                """{}'s owns {} shares of {}""".format(message.author, current["qty"], symbol.upper()))
        except Exception as e:
            print(e)
            await message.channel.send("You don't own this stock, {}.".format(str(message.author)))


    if message.content.startswith('!p'):
        try:
            def formatStock(stock):
                symbol = stock["symbol"]
                shares = stock["shares"]
                total_value = float(current_price(symbol)) * shares
                result =  """{}: {:,.2f} shares (currently ${:,.2f})\n""".format(symbol, shares, total_value)
                return result
            portfolio = get_portfolio(message.author)
            if (len(portfolio) == 0):
                return await message.channel.send("Your portfolio is empty, {}".format(str(message.author)))
            result = "".join(map(formatStock, portfolio))
            await message.channel.send(
                """{}'s Portfolio: \n{}""".format(message.author, result))
        except Exception as e:
            print(e)
            await message.channel.send("{}'s portfolio could not be found.",format(str(message.author)))



client.run(DISCORD_TOKEN)
