import logging
import os
import sys
from logging.handlers import RotatingFileHandler
import texts_bot
import datetime
# from pathlib import Path


# костыль 1 - добавить в системные пути абсолютный путь
# sys.path.append(r'/Users/yury/Dev/projects/rate_scrapper_bot')

# костыль 2 - добавить parent
# надо от этого избавиться
# parent = os.path.abspath('.')
# sys.path.insert(1, parent)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(BASE_DIR)
sys.path.append(BASE_DIR)
# print(sys.path,'syspath')

from rate_scrapper.rate_ext import get_rate, update_database
from dotenv import load_dotenv
from telegram import (Bot, ReplyKeyboardMarkup,
                      ReplyKeyboardRemove, Update,
                      InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (Updater, Filters, MessageHandler,
                          CommandHandler, ConversationHandler,
                          ContextTypes, CallbackQueryHandler)

import telegramcalendar


load_dotenv()
TG_TOKEN_BOT = os.getenv('TG_TOKEN')

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
bot = Bot(token=TG_TOKEN_BOT)
updater = Updater(token=TG_TOKEN_BOT)

CURRENCY, DATE = range(2)
ALL_CURRENCIES_LIST: list = [
    'USD', 'EUR', 'CHF', 'RUB'
]
MAIN_MENU_KEYBOARD: list = [
        ['/rate_on_date'],
        ['/rate_for_month'],
        ['/rate_year_to_date'],
        ['/update', '/start', '/cancel'],
]


def wake_up(update: Update, context: ContextTypes):
    logger.info('User woke up the bot')
    button = ReplyKeyboardMarkup(MAIN_MENU_KEYBOARD,
                                 resize_keyboard=True,
                                 one_time_keyboard=True)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        reply_markup=button,
        text=texts_bot.HELLO_MESSAGE
    )


def format_query_to_msg(query):
    res_msg: str = ''
    for key, value in query[0].items():
        res_msg += f'{key}: {value} \r\n'

    date_start: str = query[1]
    date_end: str = query[2]

    if date_start == date_end:
        text = f'Курсы на {date_start}\r\n \r\n{res_msg}'
    else:
        text = f'Курсы с {date_start} по {date_end}\r\n \r\n{res_msg}'
    return text


def choose_date_calendar(update: Update, context: ContextTypes):
    update.message.reply_text('Выберите дату',
                              reply_markup=telegramcalendar.create_calendar())
    return DATE


def inline_date_handler(update: Update, context: ContextTypes):
    logger.info(f'func inline {update.callback_query.from_user}')
    selected, date = telegramcalendar.process_calendar_selection(update,
                                                                 context)
    if selected:
        try:
            caller = 'rate_on_date_calend'
            logger.info(f'call res: {(date, caller)}')
            query_rates: tuple = get_rate(date_rate=date,
                                          currency=ALL_CURRENCIES_LIST,
                                          caller=caller)
            logger.info(f'called res {query_rates}')

            if query_rates is None:
                logger.warning(f'result is empty {query_rates}')
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text='Вернулся пустой результат, проверьте целостность БД'
                )
                return ConversationHandler.END
            msg: str = format_query_to_msg(query_rates)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=msg
            )
            return ConversationHandler.END
        except Exception as er:
            raise Exception(er)


def rate_year_to_date(update: Update, context: ContextTypes):
    logger.info('rate_year_to_date func called')
    currency = ALL_CURRENCIES_LIST # это явно лишнее
    try:
        button = ReplyKeyboardMarkup(keyboard=MAIN_MENU_KEYBOARD,
                                     resize_keyboard=True)
        chat = update.effective_chat
        date_rate = ''

        if update.message['text'] == '/rate_year_to_date':
            caller = 'rate_year_to_date'

        logger.info(f'call find_rate with args:'
                    f'{date_rate}, {ALL_CURRENCIES_LIST}, {caller}')

        logger.info(f'call res: {(date_rate, currency, caller)}')
        query_rates: tuple = get_rate(date_rate, currency, caller)
        logger.info(f'called res {query_rates}')
        msg: str = format_query_to_msg(query_rates)

        context.bot.send_message(
            chat_id=chat.id,
            reply_markup=button,
            text=msg
        )
    except Exception as er:
        raise Exception(er)


def update_today(update: Update, context: ContextTypes):
    try:
        button = ReplyKeyboardMarkup(MAIN_MENU_KEYBOARD,
                                     resize_keyboard=True)
        logger.info('вызываем update_database')
        update_database()
        logger.info('успешное обновление данных')
        update.message.reply_text('добавили в БД данные на сегодня',
                                  reply_markup=button)
    except Exception as er:
        logger.error(er)


# def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
async def cancel(update: Update) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info(f'User {user.first_name} canceled the conversation.')

    # TODO не работает отправка
    await update.message.reply_text(
        texts_bot.AFTER_CANCEL,
        reply_markup=ReplyKeyboardMarkup(MAIN_MENU_KEYBOARD))
    return ConversationHandler.END


def choose_month_calendar(update: Update, context):
    chat = update.effective_chat
    text = 'Выберите месяц'
    context.bot.send_message(
            chat_id=chat.id,
            text=text,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=telegramcalendar.month_keyboard),
        )
    return True


def inline_month_handler(update: Update, context):
    query = update.callback_query
    query.answer()
    caller = 'rate_for_month'
    date_rate = query.data
    currency = ALL_CURRENCIES_LIST

    logger.info(f'call res: {(date_rate, currency, caller)}')
    query_rates: tuple = get_rate(date_rate, currency, caller)
    logger.info(f'called res {query_rates}')

    msg: str = format_query_to_msg(query_rates)
    logger.info(f'resulted in msg {msg}')

    chat = update.effective_chat
    context.bot.send_message(
        chat_id=chat.id,
        text=f'{msg}',
    )


def main():
    logger.info('bot is running')
    print('bot is running')
    updater.dispatcher.add_handler(CommandHandler('start', wake_up), 1)
    updater.dispatcher.add_handler(CommandHandler('update', update_today), 1)
    updater.dispatcher.add_handler(CommandHandler('rate_year_to_date',
                                                  rate_year_to_date), 1)

    updater.dispatcher.add_handler(ConversationHandler(
        entry_points=[
            CommandHandler('rate_on_date', choose_date_calendar),
        ],
        states={
            DATE: [CallbackQueryHandler(inline_date_handler), ]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_message=False
        ))

    updater.dispatcher.add_handler(ConversationHandler(
        entry_points=[
            CommandHandler('rate_for_month', choose_month_calendar),
        ],
        states={
            DATE: [CallbackQueryHandler(inline_month_handler), ]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_message=False
        ))
    updater.start_polling()


if __name__ == '__main__':
    main()
