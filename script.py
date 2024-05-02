# Use environment "tele-stock-bot"
import os
import time
from datetime import datetime
# from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext
from telegram.ext import Updater, CommandHandler, CallbackContext, JobQueue
from telegram import Update, Bot
import keys
import requests
from asyncio import Queue

def start(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    context.job_queue.run_repeating(send_price, interval=3, first=0, context=chat_id)
    update.message.reply_text('Hourly messages started!')
    # update.message.reply_text("Bot has started. Hourly updates for: NVDA")

def send_price(context: CallbackContext):
    job = context.job
    context.bot.send_message(chat_id=job.context, text="hi")

    
async def get_price(update: Update, context: CallbackContext):
    data = retrieve_price()
    await update.message.reply_text(f"""
Latest price for {data["symb"]}: {data["price"]}
Open: {data["open"]}
Prev. Close: {data["prev_close"]}
Low: {data["low"]}
High: {data["high"]}""")


def retrieve_price():
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=NVDA&apikey={keys.ALPHA_API_KEY}"
    r = requests.get(url)
    data = r.json()

    # Parse data
    price_data = {}
    price_data["symb"] = data["Global Quote"]["01. symbol"]
    price_data["open"] = data["Global Quote"]["02. open"]
    price_data["high"] = data["Global Quote"]["03. high"]
    price_data["low"] = data["Global Quote"]["04. low"]
    price_data["price"] = data["Global Quote"]["05. price"]
    price_data["prev_close"] = data["Global Quote"]["08. previous close"]

    return price_data

def main() -> None:
    retrieve_price()

    # # Start the bot
    # application = ApplicationBuilder().token(keys.BOT_TOKEN).build()

    # # Command handlers
    # application.add_handler(CommandHandler("start", start))
    # application.add_handler(CommandHandler("get", get_price))

    # application.run_polling()

    # Initialize bot and handlers
    bot = Bot(keys.BOT_TOKEN)
    queue = Queue()
    updater = Updater(bot, queue)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))

    # Start the bot
    updater.start_polling()

    # Run till terminate
    updater.idle()


if __name__ == "__main__":
    main()