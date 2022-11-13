import os
import pandas as pd
import requests
from bs4 import BeautifulSoup

request = requests.get('http://iotdata.iotstorage.su/viewer.php?carid=3212')
data = request.text
soup = BeautifulSoup(data, 'lxml')
data_all_code = soup.find_all('code')

data_col_names = data_all_code[20].text.split('&')
columns_names = [data.split('=')[0] for data in data_col_names]

data_all = []
for elem in data_all_code:
    elem = elem.text.split('&')
    data_all.append([data.split('=')[1] for data in elem])

index = [x for x in range(1, len(data_all)+1)]
result_data = pd.DataFrame(data_all, index, columns_names)
result_data = result_data.sort_values(by='carid')

if not os.path.isdir('c://IOTdata'):
    os.makedirs('c://IOTdata')
result_data.to_csv('c://IOTdata/IOTdata.csv')
writer = pd.ExcelWriter('c://IOTdata/IOTdata.xlsx')
result_data.to_excel(writer)
writer.save()

print('Completed, dir: c://IOTdata')
