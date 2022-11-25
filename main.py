import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import xlsx_maker
import PySimpleGUI as sg
import configparser

link = ''
carid_str = ''
d_start_str = ''
d_finish_str = ''

try:
    input_data = configparser.ConfigParser()
    input_data.read('input.ini')
    link = input_data.get('input_data', 'link')
    carid_str = input_data.get('input_data', 'carid')
    carid_list = input_data.get('input_data', 'carid').split()
    d_start_str = input_data.get('input_data', 'd_start')
    d_finish_str = input_data.get('input_data', 'd_finish')
    d_start = pd.to_datetime(d_start_str)
    d_finish = pd.to_datetime(d_finish_str)
finally:
    sg.theme('DarkAmber')

    layout = [  [sg.InputText(key='-link-', default_text = link), sg.Text('Ссылка')],
                [sg.InputText(key='-carid-', default_text= carid_str), sg.Text('Буи (id через пробел)')],
                [sg.InputText(key='-d_start-', default_text= d_start_str), sg.Text('Начало (гггг-мм-дд чч:мм:сс)')],
                [sg.InputText(key='-d_stop-', default_text= d_finish_str), sg.Text('Конец (гггг-мм-дд чч:мм:сс)')],
                [sg.ProgressBar(max_value=100000, orientation='h', size=(30,15), key='-PROG-'), sg.Text('Обработка данных')],
                [sg.Button('Старт')]  ]

    window = sg.Window('Ввод данных', layout)

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED:
            break

        if event == 'Старт':
            link = values['-link-']
            carid_list = values['-carid-'].split()
            d_start = pd.to_datetime(values['-d_start-'])
            d_finish = pd.to_datetime(values['-d_stop-'])

            if link == '':
                sg.popup('проверьте ini')
                break

            ini = open('input.ini', 'w')
            ini.write('[input_data]\n')
            ini.write(';ссылка\n')
            ini.write(f'link = {link}\n')
            carid_str = ''
            for carid in carid_list:
                carid_str += f'{carid} '
            ini.write(';буи\n')
            ini.write(f'carid = {carid_str}\n')
            ini.write(';начало гггг-мм-дд чч:мм:сс\n')
            ini.write(f"d_start = {values['-d_start-']}\n")
            ini.write(';конец гггг-мм-дд чч:мм:сс\n')
            ini.write(f"d_finish = {values['-d_stop-']}\n")
            ini.close()

        cur_dir = os.getcwd()

        request = requests.get(link)
        data = request.text
        soup = BeautifulSoup(data, 'lxml')
        data_all_code = soup.find_all('code')

        data_col_names = data_all_code[20].text.split('&')
        columns_names = [data.split('=')[0] for data in data_col_names]

        data_all = []
        step = 100000/len(data_all_code)
        i = 1
        for elem in data_all_code:
            elem = elem.text.split('&')
            data_all.append([data.split('=')[1] for data in elem])
            window['-PROG-'].update_bar(int(i*step))
            i += 1

        index = [x for x in range(1, len(data_all) + 1)]
        result_data = pd.DataFrame(data_all, index, columns_names)

        result_data['lat'] = result_data['lat'].astype('float')
        result_data['lon'] = result_data['lon'].astype('float')
        result_data['HDOP'] = result_data['HDOP'].astype('float')
        result_data['t_surf'] = result_data['t_surf'].astype('float')
        result_data['t_sub_surf'] = result_data['t_sub_surf'].astype('float')
        result_data['pwr_v_main'] = result_data['pwr_v_main'].astype('float')

        result_data['mdate'] = result_data['mdate'] + result_data['mtime']
        result_data.rename(columns={'mdate': 'mdate_time'}, inplace=True)
        result_data = result_data.drop(columns='mtime')
        result_data_shit = result_data[result_data['mdate_time'] == "'2000-00-00''00:00:00'"]
        result_data = result_data[result_data['mdate_time'] != "'2000-00-00''00:00:00'"]
        result_data['mdate_time'] = pd.to_datetime(result_data['mdate_time'])

        result_data = result_data.sort_values(['carid', 'mdate_time'])

        for carid in carid_list:
            xlsx_maker.xlsx_maker(carid, result_data, cur_dir, d_start, d_finish)

        window.close()




