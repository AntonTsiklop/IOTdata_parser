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

result_data['lat'] = result_data['lat'].astype('float')
result_data['HDOP'] = result_data['HDOP'].astype('float')
result_data['t_surf'] = result_data['t_surf'].astype('float')
result_data['t_sub_surf'] = result_data['t_sub_surf'].astype('float')
result_data['pwr_v_main'] = result_data['pwr_v_main'].astype('float')

result_data['mdate'] = result_data['mdate'] + result_data['mtime']
result_data.rename(columns={'mdate': 'mdate_time'}, inplace = True)
result_data = result_data.drop(columns = ['mtime'])
result_data_shit = result_data[result_data['mdate_time'] == "'2000-00-00''00:00:00'"]
result_data = result_data[result_data['mdate_time'] != "'2000-00-00''00:00:00'"]
result_data['mdate_time'] = pd.to_datetime(result_data['mdate_time'])

result_data = result_data.sort_values(['carid','mdate_time'])

if not os.path.isdir('c://IOTdata'):
    os.makedirs('c://IOTdata')

carid_unique = result_data['carid'].unique()

result_data.to_csv('c://IOTdata/IOTdata.csv', sep=";", index=False, decimal=',')
writer = pd.ExcelWriter('c://IOTdata/IOTdata.xlsx')
result_data.to_excel(writer, index=False)
writer.save()

print('Completed, dir: c://IOTdata')
