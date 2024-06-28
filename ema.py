import time
import telepot
import schedule
import pandas as pd
import yfinance as yf
import ta
from datetime import datetime

TOKEN = '7001806051:AAHJrMYXHkhXB1qh_QJtg1t5kwB2cz7a-vE'
bot = telepot.Bot(TOKEN)

watchlist = []
chat_id = None

def get_stock_data(stock):
    df = yf.download(tickers=stock, period='7d', interval='1h')
    df['EMA_15'] = ta.trend.ema_indicator(df['Close'], window=15)
    return df

def check_ema_cross(stock):
    df = get_stock_data(stock)
    if df['Close'].iloc[-1] > df['EMA_15'].iloc[-1]:
        return True
    return False

def update_watchlist():
    crossed_stocks = []
    for stock in watchlist:
        if check_ema_cross(stock):
            crossed_stocks.append(stock)
    return crossed_stocks

def send_update():
    global chat_id
    if chat_id:
        crossed_stocks = update_watchlist()
        if crossed_stocks:
            bot.sendMessage(chat_id, f"Stocks crossed EMA 15: {', '.join(crossed_stocks)}")
        else:
            bot.sendMessage(chat_id, "No stocks crossed EMA 15 in the last hour.")

def handle(msg):
    global watchlist, chat_id
    chat_id = msg['chat']['id']
    command = msg['text'].strip().lower()

    if command.startswith('/add'):
        stock = command.split()[1].upper()
        if stock not in watchlist:
            watchlist.append(stock)
            bot.sendMessage(chat_id, f"{stock} added to watchlist.")
        else:
            bot.sendMessage(chat_id, f"{stock} is already in watchlist.")

    if command.startswith('/start'):
      bot.sendMessage(chat_id, f"hello thank you to join")
    elif command.startswith('/remove'):
        stock = command.split()[1].upper()
        if stock in watchlist:
            watchlist.remove(stock)
            bot.sendMessage(chat_id, f"{stock} removed from watchlist.")
        else:
            bot.sendMessage(chat_id, f"{stock} is not in watchlist.")

    elif command == '/list':
        bot.sendMessage(chat_id, f"Current watchlist: {', '.join(watchlist)}")

    elif command == '/update':
        send_update()

    elif command == '/help':
        bot.sendMessage(chat_id, "Commands:\n/add STOCK_SYMBOL - Add stock to watchlist\n/remove STOCK_SYMBOL - Remove stock from watchlist\n/list - List all stocks in watchlist\n/update - Manually update stock list\n/help - Show help message")

def schedule_updates():
    schedule.every(5).minutes.do(send_update)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    bot.message_loop(handle)
    schedule_updates()
