# Use environment "tele-stock-bot"
import os
import time
from datetime import datetime
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext, ContextTypes
# from telegram.ext import Updater, CommandHandler, CallbackContext, JobQueue
from telegram import Update
import keys
import requests
from asyncio import Queue


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_message.chat_id
    await update.message.reply_text('Hourly messages started!')
    context.application.job_queue.run_repeating(
        send_price, interval=3, first=0, chat_id=chat_id)


async def send_price(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    data = retrieve_price()
    text = f"""
Latest price for {data["symb"]}: {data["price"]}
Open: {data["open"]}
Prev. Close: {data["prev_close"]}
Low: {data["low"]}
High: {data["high"]}
"""
    await context.bot.send_message(job.chat_id, text=text)


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

    # Start the bot
    application = ApplicationBuilder().token(keys.BOT_TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))

    application.run_polling()

    # # Initialize bot and handlers
    # bot = Bot(keys.BOT_TOKEN)
    # queue = Queue()
    # updater = Updater(bot, queue)
    # dp = updater.dispatcher

    # dp.add_handler(CommandHandler("start", start))

    # # Start the bot
    # updater.start_polling()

    # # Run till terminate
    # updater.idle()


if __name__ == "__main__":
    main()
