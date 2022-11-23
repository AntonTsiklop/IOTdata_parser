import PySimpleGUI as sg

sg.theme('DarkAmber')
# Устанавливаем цвет внутри окна
layout = [  [sg.InputText(), sg.Text('Ссылка')],
            [sg.InputText(), sg.Text('Буи (id через пробел)')],
            [sg.InputText(), sg.Text('Начало (гггг-мм-дд чч:мм:сс)')],
            [sg.InputText(), sg.Text('Конец (гггг-мм-дд чч:мм:сс)')],
            [sg.Button('Ввод')]  ]

# Создаем окно
window = sg.Window('Ввод', layout)
# Цикл для обработки "событий" и получения "значений" входных данных
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    print(values[0])
    print(values[2])
    print(values[3])
window.close()