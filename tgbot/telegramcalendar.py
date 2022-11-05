#!/usr/bin/env python3
#
# A library that allows to create an inline calendar keyboard.
# grcanosa https://github.com/grcanosa
#
"""
Base methods for calendar keyboard creation and processing.
"""

import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
import datetime
import calendar
from logging.handlers import RotatingFileHandler


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


month_keyboard: list = [
                    [InlineKeyboardButton('2022', callback_data='2022')],
                    [InlineKeyboardButton('Январь', callback_data='01.2022'),
                     InlineKeyboardButton('Февраль', callback_data='02.2022'),
                     InlineKeyboardButton('Март', callback_data='03.2022')],
                    [InlineKeyboardButton('Апрель', callback_data='04.2022'),
                     InlineKeyboardButton('Май', callback_data='05.2022'),
                     InlineKeyboardButton('Июнь', callback_data='06.2022')],
                    [InlineKeyboardButton('Июль', callback_data='07.2022'),
                     InlineKeyboardButton('Август', callback_data='08.2022'),
                     InlineKeyboardButton('Сентябрь', callback_data='09.2022')],
                    [InlineKeyboardButton('Октябрь', callback_data='10.2022'),
                     InlineKeyboardButton('Ноябрь', callback_data='11.2022'),
                     InlineKeyboardButton('Декабрь', callback_data='12.2022')],
                ]



def create_callback_data(action, year, month, day):
    """ Create the callback data associated to each button"""
    return ";".join([action, str(year), str(month), str(day)])

def separate_callback_data(data):
    """ Separate the callback data"""
    return data.split(";")


def create_calendar(year=None, month=None):
    """
    Create an inline keyboard with the provided year and month
    :param int year: Year to use in the calendar, if None the current year is used.
    :param int month: Month to use in the calendar, if None the current month is used.
    :return: Returns the InlineKeyboardMarkup object with the calendar.
    """
    now = datetime.datetime.now()
    if year == None: year = now.year
    if month == None: month = now.month
    data_ignore = create_callback_data("IGNORE", year, month, 0)
    keyboard = []
    #First row - Month and Year
    row=[]
    row.append(InlineKeyboardButton(calendar.month_name[month]+" "+str(year),callback_data=data_ignore))
    keyboard.append(row)
    #Second row - Week Days
    row=[]
    for day in ["Mo","Tu","We","Th","Fr","Sa","Su"]:
        row.append(InlineKeyboardButton(day,callback_data=data_ignore))
    keyboard.append(row)

    my_calendar = calendar.monthcalendar(year, month)
    for week in my_calendar:
        row=[]
        for day in week:
            if(day==0):
                row.append(InlineKeyboardButton(" ",callback_data=data_ignore))
            else:
                row.append(InlineKeyboardButton(str(day),callback_data=create_callback_data("DAY", year, month, day)))
        keyboard.append(row)
    #Last row - Buttons
    row=[]
    row.append(InlineKeyboardButton("<", callback_data=create_callback_data("PREV-MONTH", year, month, day)))
    row.append(InlineKeyboardButton("Сегодня", callback_data=create_callback_data('TODAY', year, month, day)))
    row.append(InlineKeyboardButton(">", callback_data=create_callback_data("NEXT-MONTH", year, month, day)))
    keyboard.append(row)

    return InlineKeyboardMarkup(keyboard)


def process_calendar_selection(update, context):
    """
    Process the callback_query. This method generates a new calendar if forward or
    backward is pressed. This method should be called inside a CallbackQueryHandler.
    :param telegram.Bot bot: The bot, as provided by the CallbackQueryHandler
    :param telegram.Update update: The update, as provided by the CallbackQueryHandler
    :return: Returns a tuple (Boolean,datetime.datetime), indicating if a date is selected
                and returning the date if so.
    """
    ret_data = (False,None)
    query = update.callback_query
    (action, year, month, day) = separate_callback_data(query.data)
    curr = datetime.datetime(int(year), int(month), 1)
    if action == "IGNORE":
        context.bot.answer_callback_query(callback_query_id=query.id)
    elif action == "TODAY":
        ret_data = True, datetime.datetime(year=datetime.datetime.now().year,
                                           month=datetime.datetime.now().month,
                                           day=datetime.datetime.now().day)
        
    elif action == "DAY":
        # context.bot.edit_message_text(text=query.message.text,
        #     chat_id=query.message.chat_id,
        #     message_id=query.message.message_id
            # )
        ret_data = True, datetime.datetime(int(year), int(month), int(day))
    elif action == "PREV-MONTH":
        pre = curr - datetime.timedelta(days=1)
        context.bot.edit_message_text(text=query.message.text,
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            reply_markup=create_calendar(int(pre.year), int(pre.month)))
    elif action == "NEXT-MONTH":
        ne = curr + datetime.timedelta(days=31)
        context.bot.edit_message_text(text=query.message.text,
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            reply_markup=create_calendar(int(ne.year), int(ne.month)))
    else:
        context.bot.answer_callback_query(callback_query_id=query.id, text="Something went wrong!")
        # UNKNOWN
    logger.info(f'process_calendar_selection returns {ret_data}')
    return ret_data
