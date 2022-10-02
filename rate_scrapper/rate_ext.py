from openpyxl import load_workbook
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
import pandas as pd
from logging.handlers import RotatingFileHandler
from datetime import date
import requests
import sqlite3
import os
import sys
import logging
from pathlib import Path


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



# links
link_first_part = 'https://nationalbank.kz/ru/exchangerates/ezhednevnye-oficialnye-rynochnye-kursy-valyut/excel?'
test_link = 'https://nationalbank.kz/ru/exchangerates/ezhednevnye-oficialnye-rynochnye-kursy-valyut/excel?rates%5B%5D=5&rates%5B%5D=6&rates%5B%5D=16&rates%5B%5D=23&beginDate=2022-09-01&endDate=2022-09-27'


DEBUG = False
url_mir = 'https://mironline.ru/support/list/kursy_mir/'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'}
tg_token = os.getenv('TG_TOKEN')

# current_list = []
id_rates = [5, 6, 16, 23] 


def form_link(id_rates, begin_date, end_date):
    """ Fuction for creating a link based on the currency input and dates """
    try:
        mystring = 'rates%5B%5D='
        currencies_list = [mystring + id + '&' for id in map(str, id_rates)]
        currencies = ''.join(currencies_list)
        return f'{link_first_part}{currencies}beginDate={begin_date}&endDate={end_date}'
    except Exception as er:
        logger.error(er)




def create_database():
    excel_file = Path(__file__).with_name('rates.xlsx')
    rates = pd.read_excel(excel_file)

    # SQLITE https://docs.python.org/3/library/sqlite3.html
    # First, we need to create a new database and open a database connection to allow sqlite3 to work with it.
    con = sqlite3.connect("rates_db.db")

    # In order to execute SQL statements and fetch results from SQL queries, we will need to use a database cursor
    cur = con.cursor()


    # https://www.dataquest.io/blog/excel-and-pandas/
    rates_to_pands = pd.ExcelFile(excel_file)
    rates_list = []
    rates_list.append(rates_to_pands.parse('Courses'))
    rates = pd.concat(rates_list)
    rates = rates.set_index('Date')
    rates.to_sql('rates_db', con, if_exists="replace")
    # or replace  https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html

def request_today_rates():
    # тянем сегодняшнюю дату и добаввляем её в request
    try:
        begin_date = date.today()
        end_date = date.today()
        
        url = form_link(id_rates, begin_date, end_date)
        print(url)
        logger.info(f'ОТПРАВЛЯЕМ запрос с url {url} и headers {headers}')
        r = requests.get(url, headers=headers)
        # response_text = r.content
        logger.info((f'ОТПРАВИЛИ запрос с url {url} и headers {headers}'))
        with open('rates_today.xlsx', 'wb') as f:
            logger.info((f'Сохраняем файл'))
            f.write(r.content)
    except Exception as er:
        logger.error(er)


def update_database():
    try:
        con = sqlite3.connect("rates_db.db")
        cur = con.cursor()
        # request_today_rates() 
        # устанавливаем соединение с существующей DB
        excel_file = Path(__file__).with_name('rates_today.xlsx')
        
    
        rates = pd.read_excel(excel_file)

        # SQLITE https://docs.python.org/3/library/sqlite3.html
        # First, we need to create a new database and open a database connection to allow sqlite3 to work with it.


        # https://www.dataquest.io/blog/excel-and-pandas/
        rates_to_pands = pd.ExcelFile(excel_file)
        rates_list = []
        rates_list.append(rates_to_pands.parse('Courses'))
        rates = pd.concat(rates_list)
        rates = rates.set_index('Date')
        rates.to_sql('rates_db', con, if_exists="append")
        # проверка на то нет ли текущей даты уже в DB
    except Exception as er:
        logger.error(er)


def rate_on_date(currency, date):
    try:
        con = sqlite3.connect("rates_db.db")
        # In order to execute SQL statements and fetch results
        # from SQL queries, we will need to use a database cursor
        cur = con.cursor()
        print('SQLite output below')
        logger.info('prepare sql query')
        list_of_currencies = ', '.join([currency])
        sql_query = f'SELECT {list_of_currencies} FROM rates_db WHERE Date="{date}"'
        logger.info(f'effective query" {sql_query}')
        cur.execute(sql_query)
        res = cur.fetchall()
        print(res)
        return res
    except Exception as er:
        logger.error(er)


def main():
    # request_today_rates()
    update_database()


if __name__ == '__main__':
    main()









"""
wb2 = load_workbook('Tue, 27 Sep 2022 07-06-04.xlsx')
print(wb2.sheetnames)

dest_filename = 'Tue, 27 Sep 2022 07-06-04.xlsx'
ws1 = wb.active
ws1.title = "range names"

for row in range(1, 40):
    ws1.append(range(600))

ws2 = wb.create_sheet(title="Pi")
ws2['F5'] = 3.14
ws3 = wb.create_sheet(title="Data")
for row in range(10, 20):
    for col in range(27, 54):
        _ = ws3.cell(column=col, row=row, value="{0}".format(get_column_letter(col)))
print(ws3['AA10'].value)
wb.save(filename = dest_filename)
"""




