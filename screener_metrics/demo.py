from pyairtable import Table
import os 
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import json

load_dotenv()

api_key = os.environ.get('API_KEY')
base = os.environ.get('BASE')
table_name = 'About'

table = Table(api_key, base, table_name)

table_values = table.all()
values = []
for row in table_values:
    values.append({'id' : row['id'], 'symbol' : row['fields']['Symbol'], 'name' : row['fields']['Name']})
n = len(values)

with sync_playwright() as p:
    browser = p.firefox.launch()
    page = browser.new_page()
    i = 0
    count = 0
    while i<n:
        try:
            page.goto("https://www.screener.in/company/" + values[i]['symbol'] + "/")
            for j in range(1,10):
                column = page.query_selector('//*[@id="top-ratios"]/li[' + str(j) + ']/span[1]')
                column = column.inner_text()
                col_value = page.query_selector('//*[@id="top-ratios"]/li[' + str(j) + ']/span[2]')
                col_value = col_value.inner_text()
                if '\u20b9' in col_value:
                    col_value = 'Rs. ' + col_value[2:]
                values[i][column] = col_value
                count = 0
        except:
            if count != 3:
                page = browser.new_page()
                i -= 1
                count += 1
        i += 1
    browser.close()

json_dict = dict()
for value in values:
    json_dict[value['symbol']] = dict()
    for x in value:
        if x != 'id' and x != 'symbol':
            json_dict[value['symbol']][x] = value[x]

with open('metrics.json','w') as f:
    json.dump(json_dict, f, indent = 4)