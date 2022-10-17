import requests
import logging
import json
import os
import sys
import re
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
# убрать лишние символы 
# может быть есть перенос по строкам 
# Попробовать переписать кнопки на классы 
# test
# Limit who can use the bot https://github.com/python-telegram-bot/python-telegram-bot/wiki/Frequently-requested-design-patterns#how-do-i-limit-who-can-use-my-bot


load_dotenv()
tg_token = os.getenv('TG_TOKEN_TEST')


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


CURRENCY, DATE, TEST = range(3)
currency = ''


def wake_up(update, context):
    logger.info('User woke up the bot')
    chat = update.effective_chat
    button = ReplyKeyboardMarkup([
        ['/rate_on_date'],
        ['/rate_for_period'],
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
        
        if (update.message['text'] == 'USD'
            or update.message['text'] == 'EUR'
            or update.message['text'] == 'CHF'
            or update.message['text'] == 'RUB'):
            
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
        # print(res, '<- it is res')
        # print(type(res))
        # json.dumps(res)
        res_msg = re.sub('[^A-Za-z0-9|А-Яа-я|.|:| ]+', '', json.dumps(res))
        
        # res_msg = f'курсы на {date_rate}:'
        # # for cur, value in res.items():
        # #     res_msg.join([f'{cur}', ':', f'{value}'])

        # for key, value in res.items():
        #     res_msg += key, value[0]
            
            
        context.bot.send_message(
            chat_id=chat.id,
            reply_markup=button,
            text=(f'на {date_rate} курсы: {res_msg}')
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
        today_rates_msg = re.sub('[^A-Za-z0-9|А-Яа-я|.|:| ]+', '', today_rates)
        update.message.reply_text(f'добавили в БД данные на сегодня: {today_rates_msg}',
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


def test_func(update, context):
    test_func2(update, context)
    return DATE


def test_func2(update, context):
    chat = update.effective_chat
    context.bot.send_message(
        chat_id=chat.id,
        text=(f'success')
    )
    return (TEST, ConversationHandler.END)
    


def main():
    logger.info('bot initiated')
    print('bot initiated')
    updater.dispatcher.add_handler(CommandHandler('update', update_today))
    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    
    # converation for getting currecny rates on a specific day
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
    
    # converation for getting currecny rates on a specific day
    updater.dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('rate_for_period', currency_pick)],
        states={
            CURRENCY: [MessageHandler(
                Filters.regex('^(USD|EUR|CHF|RUB|Все валюты)$'),
                pick_date)],
            DATE: [MessageHandler(
                Filters.regex('^([0-9]{1,2}\\.[0-9]{1,2}\\.[0-9]{4}|Сегодня)$'),
                test_func)],
            TEST: [CommandHandler('end', test_func)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        ))
    

    updater.start_polling()


if __name__ == '__main__':
    main()
