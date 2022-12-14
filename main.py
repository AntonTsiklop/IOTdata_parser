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
except:
    pass
finally:
    sg.theme('DarkAmber')

    layout = [[sg.InputText(key='-link-', default_text=link), sg.Text('Ссылка')],
              [sg.InputText(key='-carid-', default_text=carid_str), sg.Text('Буи (id через пробел)')],
              [sg.InputText(key='-d_start-', default_text=d_start_str), sg.Text('Начало (гггг-мм-дд чч:мм:сс)')],
              [sg.InputText(key='-d_stop-', default_text=d_finish_str), sg.Text('Конец (гггг-мм-дд чч:мм:сс)')],
              [sg.ProgressBar(max_value=100000, orientation='h', size=(30, 15), key='-PROG-'),
               sg.Text('Обработка данных')],
              [sg.Button('Старт'), sg.Button('Выход')]]

    window = sg.Window('Ввод данных', layout, finalize=True)

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == 'Выход':
            break

        if event == 'Старт':
            link = values['-link-']
            carid_list = values['-carid-'].split()
            d_start = pd.to_datetime(values['-d_start-'])
            d_finish = pd.to_datetime(values['-d_stop-'])

            if ((link == '') or (carid_str == '') or (d_start_str == '') or (d_finish_str == '')) and (
                    (values['-link-'] == '') or (values['-carid-'] == '') or (values['-d_start-'] == '') or (
                    values['-d_stop-'] == '')):
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
        window['-PROG-'].update_bar(10000)
        request = requests.get(link)
        data = request.text
        soup = BeautifulSoup(data, 'lxml')
        window['-PROG-'].update_bar(20000)
        data_all_code = soup.find_all('code')
        window['-PROG-'].update_bar(35000)
        columns_names = ['carid', 'lat', 'lon', 'sats', 'HDOP', 'platform_type', 'count', 't_surf', 't_sub_surf',
                            'turbidity', 'turbidity_mg',  'hp', 'submergence', 'rough', 'level_plc', 'pwr_v_main',
                            'mdate', 'mtime', 'turb_debug', 'frame', 'test']
        columns_names_rb = []
        columns_names_pb = []
        columns_names_ws = []

        data_all = []
        step = 65000 / len(data_all_code)

        for i, elem in enumerate(data_all_code):
            elem = elem.text.split('&')
            data_all.append([data.split('=')[1] for data in elem])
            window['-PROG-'].update_bar(35000 + int(i * step))

        index = [x for x in range(1, len(data_all) + 1)]
        result_data = pd.DataFrame(data_all, index, columns_names)

        if 'lat' in result_data.columns: result_data['lat'] = result_data['lat'].astype('float')
        if 'lon' in result_data.columns: result_data['lon'] = result_data['lon'].astype('float')
        if 'HDOP' in result_data.columns: result_data['HDOP'] = result_data['HDOP'].astype('float')
        if 't_surf' in result_data.columns: result_data['t_surf'] = result_data['t_surf'].astype('float')
        if 't_sub_surf' in result_data.columns: result_data['t_sub_surf'] = result_data['t_sub_surf'].astype('float')
        if 'pwr_v_main' in result_data.columns: result_data['pwr_v_main'] = result_data['pwr_v_main'].astype('float')

        result_data['mdate'] = result_data['mdate'] + result_data['mtime']
        result_data.rename(columns={'mdate': 'mdate_time'}, inplace=True)
        result_data = result_data.drop(columns='mtime')
        result_data_shit = result_data[result_data['mdate_time'] == "'2000-00-00''00:00:00'"]
        result_data = result_data[result_data['mdate_time'] != "'2000-00-00''00:00:00'"]
        result_data['mdate_time'] = pd.to_datetime(result_data['mdate_time'])

        result_data = result_data.sort_values(['carid', 'mdate_time'])

        for carid in carid_list:
            xlsx_maker.xlsx_maker(carid, result_data, cur_dir, d_start, d_finish)
        sg.popup('Обработка завершена')
    window.close()
