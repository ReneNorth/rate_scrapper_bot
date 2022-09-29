import requests
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from .rate_scrapper import rate_on_date

from dotenv import load_dotenv
from telegram import Bot, ReplyKeyboardMarkup
from telegram.ext import Updater, Filters, MessageHandler, CommandHandler

from pathlib import Path



load_dotenv()

DEBUG = False
url_mir = 'https://mironline.ru/support/list/kursy_mir/'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'}
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


# def rate_on_date(update, context):
    
    #page_text = get_page_content(url_mir)
    # тут будет вызов функции из другого файла

    
    # chat = update.effective_chat
    # context.bot.send_message(chat_id=chat.id, text=message)
    pass


def main():
    # logger.info('start')
    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(CommandHandler('get_course', rate_on_date))
    updater.start_polling()


if __name__ == '__main__':
    main()
