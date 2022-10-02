import requests
import logging
import os
import sys
import pathlib
from logging.handlers import RotatingFileHandler
from pprint import pprint

from rate_scrapper.rate_ext import rate_on_date
from tgbot.dummy import dummy
# https://realpython.com/python-import/#basic-python-import

from dotenv import load_dotenv


from aiogram.dispatcher.filters.state import StatesGroup, State

from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const


class MySG(StatesGroup):
    main = State()






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








main_window = Window(
    Const("Hello, unknown person"),  # just a constant text
    Button(Const("Useless button"), id="nothing"),  # button with text and id
    state=MySG.main,  # state is used to identify window between dialogs
)




def main():
    logger.info('start')
    pass



if __name__ == '__main__':
    main()
