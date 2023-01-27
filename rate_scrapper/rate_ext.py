from openpyxl import load_workbook
import pandas as pd
from logging.handlers import RotatingFileHandler
from datetime import date, datetime
import calendar
import requests
import sqlite3
import os
import sys
import logging
from pathlib import Path



# logger
logger = logging.getLogger(__name__)
# logging.StreamHandler(stream=sys.stdout)

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(
    format='%(asctime)s'
           '%(filename)s - %(funcName)s - %(args)s - %(lineno)d - %(levelname)s - %(message)s - %(name)s',
    level=logging.INFO,
    filename='main.log',
    filemode='a'
)
handler = RotatingFileHandler('main.log', maxBytes=50000000, backupCount=5)
logger.addHandler(handler)

# formatter = logging.Formatter(
#     '%(filename)s - %(asctime)s - %(funcName)s - %(args)s - %(lineno)d - %(levelname)s - %(message)s - %(name)s',
# )

# handler.setFormatter(formatter)



# links
link_first_part = 'https://nationalbank.kz/ru/exchangerates/ezhednevnye-oficialnye-rynochnye-kursy-valyut/excel?'
test_link = 'https://nationalbank.kz/ru/exchangerates/ezhednevnye-oficialnye-rynochnye-kursy-valyut/excel?rates%5B%5D=5&rates%5B%5D=6&rates%5B%5D=16&rates%5B%5D=23&beginDate=2022-09-01&endDate=2022-09-27'


DEBUG = False
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'}
tg_token = os.getenv('TG_TOKEN')

# current_list = []
id_rates = [5, 6, 16, 23]
rates_tname = 'rates'


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
    """ Recreates database from scratch """
    # if 'file exists':
    #    os.remove(db)
    try:
        os.remove(db)
        request_all_rates()
        excel_file = Path(__file__).with_name('rates_from_010122.xlsx')
        rates = pd.read_excel(excel_file)
        con = sqlite3.connect(db)
        cur = con.cursor()
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
    # объединить request today с requst all 
    
    # добавить проверку на дубликаты
    try:
        begin_date = date.today()
        end_date = date.today()
        url = form_link(id_rates, begin_date, end_date)
        logger.info(f'ОТПРАВЛЯЕМ запрос с url {url} и headers {headers}')
        r = requests.get(url, headers=headers)
        logger.info((f'ОТПРАВИЛИ запрос с url {url} и headers {headers}'))
        with open(os.path.join(path, 'rates_today.xlsx'), 'wb') as f:
            logger.info(('Сохраняем файл'))
            f.write(r.content)
    except Exception as er:
        logger.error(er)


def update_database():
    # улучшить логику - например,
    # проверить недостающие даты с начала периода
    try:
        request_today_rates()
        logger.info(f'подключается к базе {db} в {path}')
        con = sqlite3.connect(db)
        logger.info(f'успешное подключение {db} в {path}')
        cur = con.cursor()
        
        # задаём файл
        excel_file = Path(__file__).with_name('rates_today.xlsx')
        # read excel into pandas dataframe
        rates = pd.read_excel(excel_file)
        rates_to_pands = pd.ExcelFile(excel_file)
        rates_list = []
        rates_list.append(rates_to_pands.parse('Courses'))
        rates = pd.concat(rates_list)
        rates = rates.set_index('Date')

        rates.to_sql('rates', con, if_exists="append")
        # проверка на то нет ли текущей даты уже в DB
        db_date_change()
    except Exception as er:
        logger.error(er)
        return Exception


def replace_date(date):
    try:
        logger.info(f'got date {date}')
        if hasattr(date, 'string'):
            char = date.string
        else:
            char = date
        new_date = (f'{char[6]}{char[7]}{char[8]}{char[9]}-'
                    f'{char[3]}{char[4]}-'
                    f'{char[0]}{char[1]}')
        logger.info(f'the date now in {new_date} format')
        return new_date
    except Exception as er:
        logger.error(er)


def db_date_change():
    try:
        logger.info(f'подключается к базе {db} в {path}')
        con = sqlite3.connect(db)
        logger.info(f'успешное подключение {db} в {path}')
        cur = con.cursor()
        df = pd.read_sql_query(f'SELECT * from {rates_tname}', con)

        # regex для поиска даты
        pat = r'^([0-9]{1,2}.[0-9]{1,2}.[0-9]{4})$'
        # converting dataframe to series
        ser = df['Date'].squeeze()
        new_ser = ser.str.replace(pat, replace_date, regex=True)

        # избавляемся от id
        new_ser = new_ser.drop(columns=['id'])

        # update the initial dataframe with the new date column
        df.update(new_ser)

        # write updated dataframe to the sqlite DB
        df.to_sql(rates_tname, con, if_exists='replace', index=False)

    except Exception as er:
        logger.error(er)


def get_rate(date_rate, currency: list, caller: str=''):
    """Функция получает на вход дату и вызывающую функцию,
    подставляет необходимые значения,
    затем вызывает соответствующую функцию для запроса к базе.
    
    """
    # сейчас дата приходит из разных функций в разном формате 
    # в зависимости от того, кто вызывает 
    # TODO переделать эту логику 
    # добавить проверку даты на адекватность
    print(type(date_rate))
    print(date_rate)
    logger.info(f'caller is {caller}')
    try:
        if caller == 'rate_on_date_calend':
            new_date_rate = date_rate.strftime('%Y-%m-%d')
            begin_date = new_date_rate
            end_date = new_date_rate
            
        if caller == 'rate_on_date':
            new_date_rate = replace_date(date_rate)
            begin_date = new_date_rate
            end_date = new_date_rate
            
        if caller == 'rate_for_month':
            begin_date = f'{date_rate[3:]}-{date_rate[:2]}-01'
            last_day_month = calendar.monthrange(int(date_rate[3:]),
                                                 int(date_rate[:2]))[1]
            end_date = f'{date_rate[3:]}-{date_rate[:2]}-{last_day_month}'
            logger.info(f' begin daate {begin_date}, end date {end_date}')
                
        if caller == 'rate_year_to_date':
            current_year = date.today().strftime('%Y')
            begin_date = f'{current_year}-01-01'
            end_date = date.today()
        
        logger.info(f'args: {caller}, {begin_date}, {end_date}')
        return calc_rate(begin_date, end_date, currency)
    except Exception as er:
        logger.error(er)


# сделать тут корректные аннотации / формат проверки данных 
# может быть regex
# как правильно прописать ожидаемый формат данных?
def calc_rate(begin_date, end_date, currency):
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
            sql_query = f'SELECT "{item}" FROM rates WHERE Date BETWEEN "{begin_date}" AND "{end_date}"'
            logger.info(f'effective query: {sql_query}')
            # кладём результат запроса в dataframe
            df = pd.read_sql_query(sql_query, con)
            logger.info(f'{len(df)} - длина полученного массива')
            if len(df) == 0:
                raise Exception
            logger.info(df.head(10))
            # итерационно считаем среднее по каждой валюте и округляем до 2 знаков
            res = df[f'{item}'].mean().round(decimals=2)
            # добавляем полученное значение в словарь
            currency_dict[item] = res
            logger.info(f' результат запроса: {res}')
        if not currency_dict:
            raise Exception
        # возвращаем полученный словарь
        return currency_dict, begin_date, end_date
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
        
        # weighted_avg()
        create_database()
        db_date_change()
        # debug_func()
        # logger.info('initiated main')
        # update_database()
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
