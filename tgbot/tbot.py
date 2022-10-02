import requests
import requests
import logging
import json
import os
import sys
import pathlib
from logging.handlers import RotatingFileHandler
from pprint import pprint

from rate_scrapper.rate_ext import rate_on_date
from tgbot.dummy import dummy
# https://realpython.com/python-import/#basic-python-import

from dotenv import load_dotenv
from telegram import Bot, ReplyKeyboardMarkup
from telegram.ext import Updater, Filters, MessageHandler, CommandHandler, StringRegexHandler, ConversationHandler

from pathlib import Path


# TO DO 
# Limit who can use the bot https://github.com/python-telegram-bot/python-telegram-bot/wiki/Frequently-requested-design-patterns#how-do-i-limit-who-can-use-my-bot


# path = os.getcwd()
# print('Current Directory', path)
 
# prints parent directory
# print('Parent directory', os.path.abspath(os.path.join(path, os.pardir)))

load_dotenv()

DEBUG = False
url_mir = 'https://mironline.ru/support/list/kursy_mir/'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'}
tg_token = os.getenv('TG_TOKEN')

current_list = []


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
    filemode='w'
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



def wake_up(update, context):
    chat = update.effective_chat
    # name = update.message.chat.first_name
    # photo = requests.get(CAT_URL).json()[0].get('url')
    # вложенный список - это новый ряд кнопок
    button = ReplyKeyboardMarkup([
        ['/rate_on_date'],
        ['/start'],
    ], resize_keyboard=True)

    context.bot.send_message(
        chat_id=chat.id,
        reply_markup=button,
        text=('Отправляю курсы валют')
    )


def send_message(update, message):
    chat = update.effective_chat
    bot.send_message(chat_id=chat.id, message=message)



def get_course(update, message):
    chat = update.effective_chat
    rate = rate_on_date() # <- остановился на том, что
    # вызов функции с датой и валютами из сообщения


def currency_pick(update, context):
    chat = update.effective_chat
    # name = update.message.chat.first_name
    # photo = requests.get(CAT_URL).json()[0].get('url')
    # вложенный список - это новый ряд кнопок
    button = ReplyKeyboardMarkup([
        ['/USD', '/EUR'],
        ['/FRANK', '/RUB'],
        ['/all_currencies'],
        ['/start']
        
    ], resize_keyboard=True)

    context.bot.send_message(
        chat_id=chat.id,
        reply_markup=button,
        text=('Выбери из предложенных валют')
    )


    
def pick_date(update, context):
    try:
        chat = update.effective_chat
        #wjdata = requests.get('url').json()
        #wjdata['data']['current_condition'][0]['temp_C']
        currency = update.message['text'][1:]
        print(currency, '<- update context args')
        context.bot.send_message(
            chat_id=chat.id,
            text=(f'{currency}')
        )
        find_rate(chat, context, currency)
    except Exception as er:
        logger.error(f'{er}')
        return er


def find_rate(chat, context, currency):
    logger.info('find rate')
    try:
        context.bot.send_message(
            chat_id=chat.id,
            text=(f' {currency}, введи дату'))
    except Exception as er:
        logger.error(f'{er}')
        return er
    
def date_try(update, context):
    try:
        logger.info('date try func')
        chat = update.effective_chat
        message = update.message['text']
        context.bot.send_message(chat_id=chat.id, text=(f'{message}'))
    except Exception as er:
        logger.error(f'{er}')
        return er
    
    


# служебные функции
# async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")
    

# def rate_on_date(update, context):
    
    #page_text = get_page_content(url_mir)
    # тут будет вызов функции из другого файла

    
    # chat = update.effective_chat
    # context.bot.send_message(chat_id=chat.id, text=message)
    


def main():
    logger.info('start')
    print('MAIN <-------')
    
    
    
    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(CommandHandler('rate_on_date', currency_pick))
    updater.dispatcher.add_handler(CommandHandler('all_currencies', pick_date))
    updater.dispatcher.add_handler(CommandHandler('RUB', pick_date, pass_args=True))
    updater.dispatcher.add_handler(CommandHandler('USD', pick_date))
    updater.dispatcher.add_handler(CommandHandler('EUR', pick_date))
    updater.dispatcher.add_handler(CommandHandler('FRANK', pick_date))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex('^[0-9]{1,2}\\.[0-9]{1,2}'), date_try))
    # 3.22 or 03.22
    # https://uibakery.io/regex-library/date-regex-python
    
    # updater.dispatcher.add_handler(CommandHandler('rate_on_date', get_course))
    
    
    
    # служебные хэндлеры
    # https://github.com/python-telegram-bot/python-telegram-bot/wiki/Extensions-%E2%80%93-Your-first-Bot
    # unknown_handler = MessageHandler(filters.COMMAND, unknown)
    # application.add_handler(unknown_handler) 
    updater.start_polling()
    
    


if __name__ == '__main__':
    main()
