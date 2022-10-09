from openpyxl import load_workbook
import pandas as pd
from logging.handlers import RotatingFileHandler
from datetime import date
import requests
import sqlite3
import os
import sys
import logging
from pathlib import Path


# TO DO 
# Добавить удаление эксель файлов после обновления базы
# если такой даты нет, то сделать запрос таких данных,
# добавить в БД и вернуть ответ


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



# links
link_first_part = 'https://nationalbank.kz/ru/exchangerates/ezhednevnye-oficialnye-rynochnye-kursy-valyut/excel?'
test_link = 'https://nationalbank.kz/ru/exchangerates/ezhednevnye-oficialnye-rynochnye-kursy-valyut/excel?rates%5B%5D=5&rates%5B%5D=6&rates%5B%5D=16&rates%5B%5D=23&beginDate=2022-09-01&endDate=2022-09-27'


DEBUG = False
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'}
tg_token = os.getenv('TG_TOKEN')

# current_list = []
id_rates = [5, 6, 16, 23]


# path to DB 
path = os.path.dirname(os.path.abspath(__file__))
db = os.path.join(path, 'rates_db.db')


def form_link(id_rates, begin_date, end_date):
    """ Fuction for creating a link based on the currency input and dates """
    try:
        mystring = 'rates%5B%5D='
        currencies_list = [mystring + id + '&' for id in map(str, id_rates)]
        currencies = ''.join(currencies_list)
        return f'{link_first_part}{currencies}beginDate={begin_date}&endDate={end_date}'
    except Exception as er:
        logger.error(er)


def request_all_rates():
    try:
        begin_date = '01.01.2022'
        end_date = date.today()
        url = form_link(id_rates, begin_date, end_date)
        logger.info(f'ОТПРАВЛЯЕМ запрос с url {url} и headers {headers}')
        r = requests.get(url, headers=headers)
        # response_text = r.content
        logger.info((f'ОТПРАВИЛИ запрос с url {url} и headers {headers}'))
        with open(os.path.join(path, 'rates_from_010122.xlsx'), 'wb') as f:
            logger.info((f'Сохраняем файл'))
            f.write(r.content)
    except Exception as er:
        logger.error(er)
    



def create_database():
    # if 'file exists':
    #    os.remove(db)
    try:
        os.remove(db)
        request_all_rates()
        excel_file = Path(__file__).with_name('rates_from_010122.xlsx')
        rates = pd.read_excel(excel_file)
        # SQLITE https://docs.python.org/3/library/sqlite3.html
        # First, we need to create a new database and open a database connection to allow sqlite3 to work with it.
        con = sqlite3.connect(db)
        # In order to execute SQL statements and fetch results from SQL queries, we will need to use a database cursor
        cur = con.cursor()
        # https://www.dataquest.io/blog/excel-and-pandas/
        rates_to_pands = pd.ExcelFile(excel_file)
        rates_list = []
        rates_list.append(rates_to_pands.parse('Courses'))
        rates = pd.concat(rates_list)
        rates = rates.set_index('Date')
        rates.to_sql('rates', con, if_exists='replace')
        # add sumarry about the created file
    except Exception as er:
        logger.error(f'{er}')
    # or replace  https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html

def request_today_rates():
    # тянем сегодняшнюю дату и добаввляем её в request
    try:
        begin_date ='10.10.2022'
        end_date = '10.10.2022'
        url = form_link(id_rates, begin_date, end_date)
        logger.info(f'ОТПРАВЛЯЕМ запрос с url {url} и headers {headers}')
        r = requests.get(url, headers=headers)
        logger.info((f'ОТПРАВИЛИ запрос с url {url} и headers {headers}'))
        with open(os.path.join(path, 'rates_today.xlsx'), 'wb') as f:
            logger.info((f'Сохраняем файл'))
            f.write(r.content)
    except Exception as er:
        logger.error(er)


def update_database():
    try:
        request_today_rates()
        logger.info(f'подключается к базе {db} в {path}')
        con = sqlite3.connect(db)
        logger.info(f'успешное подключение {db} в {path}')
        cur = con.cursor()
        excel_file = Path(__file__).with_name('rates_today.xlsx')
        rates = pd.read_excel(excel_file)
        rates_to_pands = pd.ExcelFile(excel_file)
        rates_list = []
        rates_list.append(rates_to_pands.parse('Courses'))
        rates = pd.concat(rates_list)
        rates = rates.set_index('Date')
        rates.to_sql('rates', con, if_exists="append")
        # проверка на то нет ли текущей даты уже в DB
    except Exception as er:
        logger.error(er)
        return Exception


def rate_on_date(currency, date_rate):
    # добавить проверку даты на адекватность
    try:
        logger.info('establish connection with the DB')
        # странно что connect создаёт файл в момент коннекшена, посмотреть как выкидывать ошибку если бд не существовало
        con = sqlite3.connect(db, check_same_thread=False)
        logger.info('connection established')
        cur = con.cursor()
        logger.info('preparing sql query')
        # list_of_currencies = ', '.join(currency)
        currency_dict = {}
        for item in currency:
            sql_query = f'SELECT {item} FROM rates WHERE Date="{str(date_rate)}"'
            logger.info(f'effective query: {sql_query}')
            cur.execute(sql_query)
            res = cur.fetchall()
            if res is None:
                raise Exception
            currency_dict[item] = res[0]
            logger.info(f' результат запроса: {res}')
        if not currency_dict:
            raise Exception
        return currency_dict
    except Exception as er:
        logger.error(er)
        
        
def debug_func():
    try:
        con = sqlite3.connect(db, check_same_thread=False)
        logger.info(f'connection to {db} established in DEBUG')
        cur = con.cursor()
        sql_query = f'SELECT Date FROM rates'
        logger.info(f'effective query: {sql_query}')
        cur.execute(sql_query)
        res = cur.fetchall()
        logger.info(f'got res: {res}')
        print(res)
        print(len(res))
    except Exception as er:
        logger.error({er})



def main():
    try:
        logger.info('started main')
        # create_database()
        # debug_func()
        # logger.info('initiated main')
        update_database()
        # logger.info('run request_today_rates func')
        logger.info('job is done')
        print('job is done')
    except Exception:
        raise Exception
    # request_today_rates()
    # update_database()
    # create_database()

if __name__ == '__main__':
    main()
