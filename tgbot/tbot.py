import requests
import logging
import os
import sys
from datetime import date
from logging.handlers import RotatingFileHandler
# костыль 1 - добавить в системные пути абсолютный путь
# sys.path.append(r'/Users/yury/Dev/projects/rate_scrapper_bot')

# костыль 2 - добавить parent
parent = os.path.abspath('.')
sys.path.insert(1, parent)

from rate_scrapper.rate_ext import rate_on_date, update_database
from dotenv import load_dotenv
from telegram import Bot, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    Filters,
    MessageHandler,
    CommandHandler,
    ConversationHandler)
from pathlib import Path


# TO DO 
# test
# Limit who can use the bot https://github.com/python-telegram-bot/python-telegram-bot/wiki/Frequently-requested-design-patterns#how-do-i-limit-who-can-use-my-bot


load_dotenv()
tg_token = os.getenv('TG_TOKEN')


# logger
logger = logging.getLogger(__name__)
logging.StreamHandler(stream=sys.stdout)

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(
    format='%(asctime)s'
           '- %(funcName)s - %(levelname)s - %(message)s - %(name)s',
    level=logging.INFO,
    filename='main.log',
    filemode='a'
)
handler = RotatingFileHandler('main.log', maxBytes=50000000, backupCount=5)
logger.addHandler(handler)

formatter = logging.Formatter(
    '%(asctime)s - %(funcName)s - %(levelname)s - %(message)s - %(name)s'
)

handler.setFormatter(formatter)


#  TG
bot = Bot(token=tg_token)
updater = Updater(token=tg_token)


CURRENCY, DATE = range(2)
currency = ''


def wake_up(update, context):
    logger.info('User woke up the bot')
    chat = update.effective_chat
    button = ReplyKeyboardMarkup([
        ['/rate_on_date'],
        ['/update'],
        ['/start'],
    ], resize_keyboard=True)

    context.bot.send_message(
        chat_id=chat.id,
        reply_markup=button,
        text=('Отправляю курсы валют. /rate_on_date вёрнет курсы валют на сегодня. '
              '/update обновит базу данных сегодняшними данными. Если бот завис, введи /cancel.' )
    )


def currency_pick(update, context):
    chat = update.effective_chat
    button = ReplyKeyboardMarkup([
        ['USD', 'EUR'],
        ['CHF', 'RUB'],
        ['Все валюты'],
    ], resize_keyboard=True)

    context.bot.send_message(
        chat_id=chat.id,
        reply_markup=button,
        text=('Выбери из предложенных валют')
    )
    logger.info(CURRENCY, '<- вернули')
    return CURRENCY


def pick_date(update, context):
    """ Вызвается при попадании одной из валют в чат """
    user = update.message.from_user
    button = ReplyKeyboardMarkup([
        ['Сегодня'],
    ], resize_keyboard=True)
    try:
        chat = update.effective_chat
        global currency
        if update.message['text'] == 'USD' or update.message['text'] == 'EUR' or update.message['text'] == 'CHF' or update.message['text'] == 'RUB':
            currency = [update.message['text']]
        elif update.message['text'] == 'Все валюты':
            currency = ['USD', 'EUR', 'CHF', 'RUB']
        logger.info(currency, '<- currency')
        context.bot.send_message(
            chat_id=chat.id,
            reply_markup=button,
            text=(f'Введи дату в формате 01.01.22 для валют {currency}')
        )
        return DATE
    except Exception as er:
        logger.error(f'{er}')
        return er


def find_rate(update, context):
    # не DRY - эту клавиатуру вынести наружу
    # или найти способ вызвать начало диалога
    button = ReplyKeyboardMarkup([
        ['/rate_on_date'],
        ['/update'],
    ], resize_keyboard=True)
    chat = update.effective_chat
    if update.message['text'] == 'Сегодня':
        date_rate = date.today().strftime('%d.%m.%Y')
    else:
        date_rate = update.message['text']
    try:
        logger.info(f'call rate_on_date with args: {currency}, {date_rate}')
        res = rate_on_date(currency, date_rate)
        context.bot.send_message(
            chat_id=chat.id,
            reply_markup=button,
            text=(f'на {date_rate} курсы: {res}')
        )
        return ConversationHandler.END
    except Exception as er:
        logger.error(er)


def update_today(update, context):
    try:
        button = ReplyKeyboardMarkup([
            ['/rate_on_date'],
            ], resize_keyboard=True)
        logger.info('вызываем update_database')
        update_database()
        logger.info(f'успешное обновление данных')
        currency = ['USD', 'EUR', 'CHF', 'RUB']
        today_rates = rate_on_date(currency, date.today().strftime('%d.%m.%Y'))
        # date today - 2022-10-12
        # format needed 12.10.2022
        print(currency, date.today())
        print(today_rates)
        update.message.reply_text(f'добавили в БД данные на сегодня: {today_rates}',
                                  reply_markup=button,
                                  )
    except Exception as er:
        logger.error(er)

# def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
def cancel(update: Update, context):
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text("Bye! I hope we can talk again some day.",
                              reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def main():
    logger.info('bot initiated')
    print('bot initiated')
    updater.dispatcher.add_handler(CommandHandler('update', update_today))
    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('rate_on_date', currency_pick)],
        states={
            CURRENCY: [MessageHandler(
                Filters.regex('^(USD|EUR|CHF|RUB|Все валюты)$'),
                pick_date)],
            DATE: [MessageHandler(
                Filters.regex('^([0-9]{1,2}\\.[0-9]{1,2}\\.[0-9]{4}|Сегодня)$'),
                find_rate)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        ))

    updater.start_polling()


if __name__ == '__main__':
    main()
