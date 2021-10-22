from pyairtable import Table
import os 
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import time
import psycopg2

load_dotenv()

api_key = os.environ.get('API_KEY')
base = os.environ.get('BASE')
table_name = 'About'

screener_login = os.environ.get('EMAIL')
screener_password = os.environ.get('PASSWORD')

host = os.environ.get('HOST')
database = os.environ.get('DATABASE')
user = os.environ.get('USER')
password = os.environ.get('DB_PASSWORD')

table = Table(api_key, base, table_name)

conn = psycopg2.connect(
    host=host,
    database=database,
    user=user,
    password=password
)
cur = conn.cursor()

table_values = table.all()
values = []
for row in table_values:
    values.append({'id' : row['id'], 'symbol' : row['fields']['Symbol'], 'name' : row['fields']['Name']})
n = len(values)

with sync_playwright() as p:
    browser = p.chromium.launch(headless = False)
    page = browser.new_page()
    page.goto('https://www.screener.in/login/?')
    page.fill('input[name="username"]', screener_login)
    page.fill('input[name="password"]', screener_password)
    page.click('button[type="submit"]')
    i = 0
    count = 0
    while i<n:
        try:
            time.sleep(1)
            page.goto("https://www.screener.in/company/" + values[i]['symbol'] + "/")
            for j in range(1,14):
                column = page.query_selector('//*[@id="top-ratios"]/li[' + str(j) + ']/span[1]')
                column = column.inner_text()
                col_value = page.query_selector('//*[@id="top-ratios"]/li[' + str(j) + ']/span[2]')
                col_value = col_value.inner_text()
                if '\u20b9' in col_value:
                    col_value = 'Rs. ' + col_value[2:]
                values[i][column] = col_value
            count = 0
        except:
            if count != 5:
                i -= 1
                count += 1
            else:
                count = 0
        i += 1
    browser.close()
sql = '''INSERT INTO metrics (symbol,name,market_cap,current_price,high_low,stock_p_e,book_value,dividend_yield,roce,roe,face_value,debt_to_equity,eps,price_to_book_value,industry_pe)
VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) 
ON CONFLICT (symbol) 
DO 
   UPDATE SET market_cap = EXCLUDED.market_cap, current_price = EXCLUDED.current_price, high_low = EXCLUDED.high_low, stock_p_e = EXCLUDED.stock_p_e, book_value = EXCLUDED.book_value, dividend_yield = EXCLUDED.dividend_yield, roce = EXCLUDED.roce, roe = EXCLUDED.roe, face_value = EXCLUDED.face_value, debt_to_equity = EXCLUDED.debt_to_equity, eps = EXCLUDED.eps, price_to_book_value = EXCLUDED.price_to_book_value, industry_pe = EXCLUDED.industry_pe;'''
v = []
scores = ['symbol','name',"Market Cap","Current Price","High / Low","Book Value","Dividend Yield","ROCE","Stock P/E","ROE","Face Value","Debt to equity","EPS","Price to book value","Industry PE"]
for value in values:
    temp = []
    for x in scores:
        if x in value:
            temp.append(value[x])
        else:
            temp.append('')
    temp = tuple(temp)
    v.append(temp)
cur.executemany(sql,v)
cur.close()
conn.commit()
conn.close()
