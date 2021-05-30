import discord
import alpaca_trade_api as trade_api
from dotenv import load_dotenv
import os
from discord.ext import commands
from db import init_db


load_dotenv()
init_db()

ALPACA_API_KEY = os.environ.get('ALPACA_API_KEY')
ALPACA_API_SECRET = os.environ.get('ALPACA_API_SECRET')
APCA_API_BASE_URL = os.environ.get('APCA_API_BASE_URL')
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')


api = trade_api.REST(ALPACA_API_KEY, ALPACA_API_SECRET, APCA_API_BASE_URL, 'v2')

# intents = discord.Intents.default()
# intents.members = True

# bot = commands.Bot('!', intents=intents)

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


# portfolios = {
#     'lawrence': {
#         'aapl': 323748237189423718942719,
#         'google'
#     }
# }

portfolios = {}

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('~clock'):
        clock = api.get_clock()
        await message.channel.send('The market is {}'.format('open.' if clock.is_open else 'closed.'))

    if message.content.startswith('$'):
        stock = message.content[1:].upper()
        try:
            current_price(stock)
            await message.channel.send("{} is currently trading at ${:,.2f}".format(stock, current_price))
        except:
            await message.channel.send("{} is not a valid stock.".format(stock))

    if message.content.startswith('!avg '):
        stock = message.content[5:].upper()
        try:
            barset = api.get_barset(stock, 'day', limit=5)
            bars = barset[stock]
            week_open = bars[0].o
            week_close = bars[-1].c
            percent_change = (week_close - week_open) / week_open * 100
            await message.channel.send("{} moved {}% over the last 5 days".format(stock, percent_change))
        except:
            await message.channel.send("{} is not a valid stock.".format(stock))


    if message.content.startswith('!buy'):
        [_, stock, amount] = message.content.split(" ")
        try:
            shares = float(amount) / current_price(stock)
            # total -= shares * current_price

            if not portfolios[message.author]:
                portfolios[message.author] = {}

            if not portfolios[message.author][stock]:
                portfolios[message.author][stock] = 0

            portfolios[message.author][stock] += shares
            await message.channel.send("Bought {} shares of {} for ${:,.2f}.".format(shares, stock.upper(), float(amount)))
        except:
            await message.channel.send("Could not buy.")


    if message.content.startswith('!sell'):
        [_, stock, amount] = message.content.split(" ")
        try:
            shares = float(amount) / current_price(stock)
            current_shares = portfolios[message.author][stock]
            new_shares = max(0, current_shares - shares)
            portfolios[message.author][stock] = new_shares

            await message.channel.send("Sold ${:,.2f} of {}".format(float(amount), stock.upper()))
        except:
            await message.channel.send("Could not sell.")

    if message.content.startswith('!p'):
        try:
            portfolio = portfolios[message.author][stock]
            print(portfolio)
            await message.channel.send(
                """Your portfolio:
                             asdad asdasd""")
        except:
            await message.channel.send("Portfolio could not be found.")



client.run(DISCORD_TOKEN)
