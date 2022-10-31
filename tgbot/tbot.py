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
# надо от этого избавиться
parent = os.path.abspath('.')
sys.path.insert(1, parent)


from rate_scrapper.rate_ext import get_rate, update_database
from dotenv import load_dotenv
from telegram import Bot, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (Updater, Filters, MessageHandler,
                          CommandHandler, ConversationHandler,
                          ContextTypes)


load_dotenv()
tg_token = os.getenv('TG_TOKEN_TEST')

logger = logging.getLogger(__name__)
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(
    format=('%(asctime)s - %(filename)s- %(funcName)s - %(args)s - %(lineno)d '
            '- %(levelname)s - %(message)s - %(name)s'),
    level=logging.INFO,
    filename='main.log',
    filemode='a'
)
handler = RotatingFileHandler('main.log', maxBytes=50000000, backupCount=5)
logger.addHandler(handler)


#  TG
bot = Bot(token=tg_token)
updater = Updater(token=tg_token)


CURRENCY, DATE, TEST = range(3)
currency = ''
func_name = ''


MAIN_MENU_KEYBOARD: list = [
        ['/rate_on_date'],
        ['/rate_for_month'],
        ['/rate_year_to_date'],
        ['/update'],
        ['/start'],
    ]

ALL_CURRENCIES_LIST: list = ['USD', 'EUR', 'CHF', 'RUB']


def wake_up(update: Update, context: ContextTypes):
    logger.info('User woke up the bot')
    global func_name
    func_name = ''
    chat = update.effective_chat
    button = ReplyKeyboardMarkup(MAIN_MENU_KEYBOARD,
                                 resize_keyboard=True)
    context.bot.send_message(
        chat_id=chat.id,
        reply_markup=button,
        text=('Отправляю курсы валют.'
              '/rate_on_date вёрнет курсы валют на сегодня. '
              '/update обновит базу данных сегодняшними данными.'
              'Если бот завис, введи /cancel.')
    )


def pick_date(update: Update, context: ContextTypes):
    """Вызвается при попадании одной из валют в чат."""
    logger.info('we are in the pick_date function')
    global currency
    global func_name
    buttons: list = []
    text: list = []
    func_name = update['message']['text']

    try:
        if func_name == '/rate_on_date':
            text = 'Введи дату в формате 01.01.2022'
            buttons = ['Сегодня']
        elif func_name == '/rate_for_month':
            text = 'Введи месяц и год в формате 10.2022'
            buttons = ['Текущий месяц']

        button = ReplyKeyboardMarkup([
            buttons,
        ], resize_keyboard=True)

        logger.info(f'func name - {func_name}, buttons - {buttons}'
                    f'{text}')

        chat = update.effective_chat
        context.bot.send_message(
            chat_id=chat.id,
            reply_markup=button,
            text=text
        )
        return DATE
    except Exception as er:
        logger.error(f'{er}')


def find_rate(update: Update, context: ContextTypes):
    currency = ALL_CURRENCIES_LIST
    global func_name
    try:
        button = ReplyKeyboardMarkup(keyboard=MAIN_MENU_KEYBOARD,
                                     resize_keyboard=True)
        chat = update.effective_chat
        date_rate = ''
        
        if func_name == '/rate_on_date':
            caller = 'rate_on_date'
            if update.message['text'] == 'Сегодня':
                date_rate = date.today().strftime('%d.%m.%Y')
            else:
                date_rate = update.message['text']
        
        if func_name == '/rate_for_month':
            caller = 'rate_for_month'
            if update.message['text'] == 'Текущий месяц':
                date_rate = date.today().strftime('%m.%Y')
            else:
                date_rate = update.message['text']

        if update.message['text'] == '/rate_year_to_date':
            func_name = '/rate_year_to_date'
            caller = 'rate_year_to_date'

        logger.info(f'call find_rate with args:'
                    f'{date_rate}, {currency}, {caller}')
        
        res = get_rate(date_rate, currency, caller)
        print(res)
        # очищаем ответ от всех символов, кроме указанных в первом аргументе re.sub
        res_msg = re.sub('[^A-Za-z0-9|А-Яа-я|.|:| ]+', '', json.dumps(res[0]))
        date_start = res[1]
        date_end = res[2]
        
        if date_start == date_end:
            text = f'Курсы на {res[1]}\r\n \r\n{res_msg}'
        else:
            text = f'Курсы с {res[1]} по {res[2]}\r\n \r\n{res_msg}'

        context.bot.send_message(
            chat_id=chat.id,
            reply_markup=button,
            # text=f'{res_msg}'
            text=text
        )
        return ConversationHandler.END
    except Exception as er:
        logger.error(er)


def update_today(update: Update, context: ContextTypes):
    try:
        button = ReplyKeyboardMarkup(MAIN_MENU_KEYBOARD,
                                     resize_keyboard=True)

        logger.info('вызываем update_database')
        update_database()
        logger.info('успешное обновление данных')

        currency = ['USD', 'EUR', 'CHF', 'RUB']

        update.message.reply_text('добавили в БД данные на сегодня',
                                  reply_markup=button)
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
    updater.dispatcher.add_handler(CommandHandler('rate_year_to_date',
                                                  find_rate))


    updater.dispatcher.add_handler(ConversationHandler(
        entry_points=[
            CommandHandler('rate_on_date', pick_date),
            CommandHandler('rate_for_month', pick_date),
        ],
        states={
            DATE: [MessageHandler(
                Filters.regex(
                    '^([0-9]{1,2}\\.[0-9]{1,2}\\.[0-9]{4}|Сегодня|Текущий месяц|[0-9]{1,2}\\.[0-9]{4})$'
                ),
                find_rate)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        ))

    updater.start_polling()


if __name__ == '__main__':
    main()
