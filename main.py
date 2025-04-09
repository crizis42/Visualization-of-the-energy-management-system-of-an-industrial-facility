from tkinter import *
from tkinter.filedialog import askopenfilenames
from tkinter.messagebox import showinfo, showerror
from PIL import Image, ImageTk 
import ctypes #Подключаем типы из С/С++
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta #изменение месяца pip install python-dateutil
#from boilers import UtilizationBoiler, heat_from_temp, heat_load_distribution, heat_cost
import pandas as pd
import numpy as np


is_fullscreen = False
root = Tk()

root.title('Визуализация системы')
root['bg'] = 'black'

# Получаем ширину и высоту экрана
# Полный размер экрана (вместе с панелью задач)
user32 = ctypes.windll.user32
user32.SetProcessDPIAware()  # Учитываем масштабирование Windows
screen_width = user32.GetSystemMetrics(0)  # Ширина экрана
screen_height = user32.GetSystemMetrics(1)  # Высота экрана

# Получаем размеры рабочей области экрана (без панели задач)
# Используем системную функцию Windows SystemParametersInfoW
spi_getworkarea = 48  # Константа для получения рабочей области
rect = ctypes.wintypes.RECT()  # Структура для хранения координат рабочей области

# Заполняем структуру rect размерами рабочей области
ctypes.windll.user32.SystemParametersInfoW(spi_getworkarea, 0, ctypes.byref(rect), 0)

# Рассчитываем ширину и высоту рабочей области
work_width = rect.right - rect.left
work_height = rect.bottom - rect.top

# Устанавливаем размеры и положение окна в пределах рабочей области
# {ширина}x{высота}+{смещение по X}+{смещение по Y}
root.geometry(f'{work_width}x{work_height}+{rect.left}+{rect.top}')

w = work_width
h = work_height #Переопределение рабочей области

def open_excel_files():
    filepaths = askopenfilenames(filetypes=[("Excel files", "*.xlsx")])  # Выбираем только .xlsx файлы

    if not filepaths:
        return  # Если ничего не выбрали — выходим из функции

    try:
        if len(filepaths) != 3:
            showerror("Ошибка!", "Необходимо выбрать ровно 3 Excel файла!")
            return

        # Объявляем переменные глобальными
        global energy_usage_data, gtu_data, gas_data, months, gas_prices

        # Пути к выбранным файлам
        energy_usage_path = filepaths[0]
        gtu_path = filepaths[1]
        gas_path = filepaths[2]

        # Загружаем данные
        energy_usage_data = pd.read_excel(energy_usage_path)
        gtu_data = pd.read_excel(gtu_path)
        gas_data = pd.read_excel(gas_path, sheet_name='Лист1', header=None)

        # Обработка файла с ценами на газ
        last_col = gas_data.loc[2, 1:].last_valid_index()  # Последняя заполненная колонка
        months = gas_data.loc[0, 1:last_col].to_numpy()    # Месяцы
        gas_prices = gas_data.loc[2, 1:last_col].to_numpy()  # Цены на газ

        print("Файлы успешно загружены!")
        print("energy_usage_data:\n", energy_usage_data.head())
        print("gtu_data:\n", gtu_data.head())
        print("gas_prices:\n", gas_prices)

        showinfo("Успех!", "Файлы успешно загружены!")

    except Exception as e:
        showerror("Ошибка!", f"Ошибка при загрузке файлов:\n{e}")

# Читаем данные
current_date = datetime.now().date()

def price_calc():
    global price
    price = 0  # Сначала обнуляем цену газа
    
    # Текущая дата
    current_day = current_date.day
    current_month = current_date.month
    current_year = current_date.year


    if 'gas_prices' not in globals():
        print("Цены на газ ещё не загружены.")
        return

    # Проверяем год и рассчитываем цену только если есть данные
    if current_year == 2024:
        if current_month <= len(gas_prices):
            price = gas_prices[current_month - 1]
    elif current_year == 2025:
        price = gas_prices[-1]
    elif current_year == 2026:
        price = gas_prices[-1]
    else:
        price = 0  # Нет данных на этот год

    # Вывод в терминал
    if price != 0:
        print(f'Стоимость газа на {current_day}.{current_month}.{current_year} = {price / 1000:.3f} руб/тыс.м3')
    else:
        print(f'Нет данных для расчета стоимости газа за {current_month}.{current_year}')

    

def fullscreen(event):
    global is_fullscreen
    is_fullscreen = not is_fullscreen
    root.attributes('-fullscreen', is_fullscreen)


# Загрузка и масштабирование изображения
def load_scaled_image(path, size):
    img = Image.open(path)
    img = img.resize((int(size), int(size)), Image.LANCZOS) 
    return ImageTk.PhotoImage(img)

def update_label():
    date_label.config(text=current_date.strftime("%d.%m.%Y"), fg='white', bg='black', font=('Arial', 14, 'bold'))

def next_date():
    global current_date
    current_date += timedelta(days=1)
    update_label()
    price_calc()

def previous_date():
    global current_date
    current_date -= timedelta(days=1)
    update_label()
    price_calc()

def next_month():
    global current_date
    current_date += relativedelta(months=1)
    update_label()
    price_calc()

def previous_month():
    global current_date
    current_date -= relativedelta(months=1)
    update_label()
    price_calc()

###################################################################################
price = None
root.bind('<F11>', fullscreen)

# Создаем холст (Canvas) для рисования
canvas = Canvas(root, bg='black', highlightthickness=0)
canvas.place(x=0, y=0, width=w, height=h)  # Растягиваем на весь экран

# Установки ГТУ
marginG = w * 0.02  # Отступы
sizeG = w * 0.09  # Размер
num_gtu = 9 # Кол-во ГТУ
widthG = num_gtu * sizeG + (num_gtu - 1) * marginG #Расчитываем ширину

xG = (w - widthG) / 2
yG = w * 0.015       # Начальная координата Y

gtu_on = load_scaled_image("img/GTU_on.png", sizeG)
gtu_off = load_scaled_image("img/GTU_off.png", sizeG)
gtu_repair = load_scaled_image("img/GTU_repair.png", sizeG)
    
# Создаем 9 изображений ГТУ
GTU_dict = {
    1: {'id': canvas.create_image(xG, yG, image=gtu_on, anchor="nw"), 
       'coords': (xG, yG)},
    2: {'id': canvas.create_image(xG + (sizeG + marginG)*1, yG, image=gtu_on, anchor="nw"),
       'coords': (xG + (sizeG + marginG)*1, yG)},
    3: {'id': canvas.create_image(xG + (sizeG + marginG)*2, yG, image=gtu_on, anchor="nw"),
       'coords': (xG + (sizeG + marginG)*2, yG)},
    4: {'id': canvas.create_image(xG + (sizeG + marginG)*3, yG, image=gtu_on, anchor="nw"),
       'coords': (xG + (sizeG + marginG)*3, yG)},
    5: {'id': canvas.create_image(xG + (sizeG + marginG)*4, yG, image=gtu_on, anchor="nw"),
       'coords': (xG + (sizeG + marginG)*4, yG)},
    6: {'id': canvas.create_image(xG + (sizeG + marginG)*5, yG, image=gtu_on, anchor="nw"),
       'coords': (xG + (sizeG + marginG)*5, yG)},
    7: {'id': canvas.create_image(xG + (sizeG + marginG)*6, yG, image=gtu_on, anchor="nw"),
       'coords': (xG + (sizeG + marginG)*6, yG)},
    8: {'id': canvas.create_image(xG + (sizeG + marginG)*7, yG, image=gtu_on, anchor="nw"),
       'coords': (xG + (sizeG + marginG)*7, yG)},
    9: {'id': canvas.create_image(xG + (sizeG + marginG)*8, yG, image=gtu_on, anchor="nw"),
       'coords': (xG + (sizeG + marginG)*8, yG)}
}

# Худ для ГТУ
colorG = "#f0f0f0" #Настройка цвета
widthG = 3 #Настройка толщины обводки
shiftG = w * 0.1 #Настройка сдвига худа (по умолчанию находится на месте самого ГТУ)

GTU_huds = {
    1: {
        'rect': canvas.create_rectangle(xG, yG + shiftG, xG + sizeG, yG + shiftG + sizeG, outline=colorG, width=widthG),
        'coords': (xG, yG + shiftG)
    },
    2: {
        'rect': canvas.create_rectangle(xG + (sizeG + marginG)*1, yG + shiftG, xG + sizeG + (sizeG + marginG)*1, yG + shiftG + sizeG, outline=colorG, width=widthG),
        'coords': (xG + (sizeG + marginG)*1, yG + shiftG)
    },
    3: {
        'rect': canvas.create_rectangle(xG + (sizeG + marginG)*2, yG + shiftG, xG + sizeG + (sizeG + marginG)*2, yG + shiftG + sizeG, outline=colorG, width=widthG),
        'coords': (xG + (sizeG + marginG)*2, yG + shiftG)
    },
    4: {
        'rect': canvas.create_rectangle(xG + (sizeG + marginG)*3, yG + shiftG, xG + sizeG + (sizeG + marginG)*3, yG + shiftG + sizeG, outline=colorG, width=widthG),
        'coords': (xG + (sizeG + marginG)*3, yG + shiftG)
    },
    5: {
        'rect': canvas.create_rectangle(xG + (sizeG + marginG)*4, yG + shiftG, xG + sizeG + (sizeG + marginG)*4, yG + shiftG + sizeG, outline=colorG, width=widthG),
        'coords': (xG + (sizeG + marginG)*4, yG + shiftG)
    },
    6: {
        'rect': canvas.create_rectangle(xG + (sizeG + marginG)*5, yG + shiftG, xG + sizeG + (sizeG + marginG)*5, yG + shiftG + sizeG, outline=colorG, width=widthG),
        'coords': (xG + (sizeG + marginG)*5, yG + shiftG)
    },
    7: {
        'rect': canvas.create_rectangle(xG + (sizeG + marginG)*6, yG + shiftG, xG + sizeG + (sizeG + marginG)*6, yG + shiftG + sizeG, outline=colorG, width=widthG),
        'coords': (xG + (sizeG + marginG)*6, yG + shiftG)
    },
    8: {
        'rect': canvas.create_rectangle(xG + (sizeG + marginG)*7, yG + shiftG, xG + sizeG + (sizeG + marginG)*7, yG + shiftG + sizeG, outline=colorG, width=widthG),
        'coords': (xG + (sizeG + marginG)*7, yG + shiftG)
    },
    9: {
        'rect': canvas.create_rectangle(xG + (sizeG + marginG)*8, yG + shiftG, xG + sizeG + (sizeG + marginG)*8, yG + shiftG + sizeG, outline=colorG, width=widthG),
        'coords': (xG + (sizeG + marginG)*8, yG + shiftG)
    }
}

# Функция для отображения текста в нужных ГТУ
def GTU_info (num, wt, prcnt, hTO, hKR, state):

    center_x, center_y = GTU_huds[num]["coords"]
    center_x += (w * 0.005)
    center_y += (w * 0.003)

    
    lines = [
        f"Номер ГТУ: {num}",
        f"Номинальная W: {wt}Квт",
        f"Уровень загрузки: {prcnt}%",
        f"Моточасы до ТО: {hTO}ч",
        f"Моточасы до КР: {hKR}ч",
    ]
    line_height = int(w * 0.015)  # Высота строки

    for i, line in enumerate(lines):
        canvas.create_text(
            center_x,
            center_y + i * line_height,
            text=line,
            anchor="nw",
            fill="white",
            font=("Arial", int(h*0.01))
        )
    x, y = GTU_dict[num]["coords"]
    if state == "on":
        canvas.create_image(x, y, image=gtu_on, anchor="nw")
    elif state == "off":
        canvas.create_image(x, y, image=gtu_off, anchor="nw")
    elif state == "repair":
        canvas.create_image(x, y, image=gtu_repair, anchor="nw")
    
GTU_info (6, 1, 1, 1, 1, "off")


# Котлы
marginB = w * 0.02  # Отступы
sizeB = w * 0.09  # Размер
num_blr = 6 # Кол-во котлов
widthB = num_blr * sizeB + (num_blr - 1) * marginB #Расчитываем ширину

xB = xG      # Начальная координата X
yB = w * 0.26     # Начальная координата Y

boiler_on = load_scaled_image("img/Boiler_on.png", sizeG)
boiler_off = load_scaled_image("img/Boiler_off.png", sizeG)

# Создаем 6 изображений Котлов
BLR_dict = {
    1: {
        'id': canvas.create_image(xB, yB, image=boiler_on, anchor="nw"),
        'coords': (xB, yB)
    },
    2: {
        'id': canvas.create_image(xB + (sizeB + marginB)*1, yB, image=boiler_on, anchor="nw"),
        'coords': (xB + (sizeB + marginB)*1, yB)
    },
    3: {
        'id': canvas.create_image(xB + (sizeB + marginB)*2, yB, image=boiler_on, anchor="nw"),
        'coords': (xB + (sizeB + marginB)*2, yB)
    },
    4: {
        'id': canvas.create_image(xB + (sizeB + marginB)*3, yB, image=boiler_on, anchor="nw"),
        'coords': (xB + (sizeB + marginB)*3, yB)
    },
    5: {
        'id': canvas.create_image(xB + (sizeB + marginB)*4, yB, image=boiler_on, anchor="nw"),
        'coords': (xB + (sizeB + marginB)*4, yB)
    },
    6: {
        'id': canvas.create_image(xB + (sizeB + marginB)*5, yB, image=boiler_on, anchor="nw"),
        'coords': (xB + (sizeB + marginB)*5, yB)
    }
}


# Худ для Котлов
colorB = "#f0f0f0" #Настройка цвета
widthB = 3 #Настройка толщины обводки
shiftB = w * 0.1 #Настройка сдвига худа (по умолчанию находится на месте самого ГТУ)

BLR_huds = {
    1: {
        'rect': canvas.create_rectangle(xB, yB + shiftB, xB + sizeB, yB + shiftB + sizeB, outline=colorB, width=widthB),
        'coords': (xB, yB + shiftB)
    },
    2: {
        'rect': canvas.create_rectangle(xB + (sizeB + marginB)*1, yB + shiftB, xB + sizeB + (sizeB + marginB)*1, yB + shiftB + sizeB, outline=colorB, width=widthB),
        'coords': (xB + (sizeB + marginB)*1, yB + shiftB)
    },
    3: {
        'rect': canvas.create_rectangle(xB + (sizeB + marginB)*2, yB + shiftB, xB + sizeB + (sizeB + marginB)*2, yB + shiftB + sizeB, outline=colorB, width=widthB),
        'coords': (xB + (sizeB + marginB)*2, yB + shiftB)
    },
    4: {
        'rect': canvas.create_rectangle(xB + (sizeB + marginB)*3, yB + shiftB, xB + sizeB + (sizeB + marginB)*3, yB + shiftB + sizeB, outline=colorB, width=widthB),
        'coords': (xB + (sizeB + marginB)*3, yB + shiftB)
    },
    5: {
        'rect': canvas.create_rectangle(xB + (sizeB + marginB)*4, yB + shiftB, xB + sizeB + (sizeB + marginB)*4, yB + shiftB + sizeB, outline=colorB, width=widthB),
        'coords': (xB + (sizeB + marginB)*4, yB + shiftB)
    },
    6: {
        'rect': canvas.create_rectangle(xB + (sizeB + marginB)*5, yB + shiftB, xB + sizeB + (sizeB + marginB)*5, yB + shiftB + sizeB, outline=colorB, width=widthB),
        'coords': (xB + (sizeB + marginB)*5, yB + shiftB)
    }
}

# Функция для отображения текста в нужных ГТУ
def BLR_info(num, prcnt, pwr, state):
    # Удаляем ВЕСЬ старый текст этого ГТУ по единому тегу
    canvas.delete(f"gtu_text_{num}")
    
    # Получаем координаты
    center_x, center_y = BLR_huds[num]["coords"]
    center_x += (w * 0.005)
    center_y += (w * 0.003)
    
    lines = [
        f"Номер котла: {num}",
        f"Уровень загрузки: {prcnt}%",
        f"Мощность: {pwr}Квт"
    ]
    
    # Создаем весь текст с ОДНИМ ОБЩИМ ТЕГОМ
    for i, line in enumerate(lines):
        canvas.create_text(
            center_x,
            center_y + i * int(w * 0.015),
            text=line,
            anchor="nw",
            fill="white",
            font=("Arial", int(h*0.01)),
            tags=f"gtu_text_{num}"  # Единый тег для всех строк
        )
    
    x, y = BLR_dict[num]["coords"]
    if state == "on":
        canvas.create_image(x, y, image=boiler_on, anchor="nw")
    elif state == "off":
        canvas.create_image(x, y, image=boiler_off, anchor="nw")

BLR_info(3, 100, 1000, "off")

# Константы для кнопок управления датой
BUTTON_WIDTH = 17  # Ширина в символах
BUTTON_HEIGHT = 1   # Высота в линиях текста
BUTTON_FONT = ('Arial', 10)  # Шрифт для кнопок

# Создаем фрейм для группировки кнопок управления датой
date_control_frame = Frame(root, bg='black')
date_control_frame.place(relx=0.02, rely=0.95, anchor=SW)  # Фиксируем в нижнем левом углу

# Создаем кнопки внутри фрейма
previous_month_button = Button(date_control_frame, text='Предыдущий месяц', 
                            command=previous_month, 
                            width=BUTTON_WIDTH, 
                            height=BUTTON_HEIGHT,
                            font=BUTTON_FONT)
previous_month_button.pack(side=LEFT, padx=5, pady=2)

previous_date_button = Button(date_control_frame, text='Предыдущий день', 
                            command=previous_date, 
                            width=BUTTON_WIDTH, 
                            height=BUTTON_HEIGHT,
                            font=BUTTON_FONT)
previous_date_button.pack(side=LEFT, padx=5, pady=2)

next_date_button = Button(date_control_frame, text='Следующий день', 
                        command=next_date, 
                        width=BUTTON_WIDTH, 
                        height=BUTTON_HEIGHT,
                        font=BUTTON_FONT)
next_date_button.pack(side=LEFT, padx=5, pady=2)

next_month_button = Button(date_control_frame, text='Следующий месяц', 
                        command=next_month, 
                        width=BUTTON_WIDTH, 
                        height=BUTTON_HEIGHT,
                        font=BUTTON_FONT)
next_month_button.pack(side=LEFT, padx=5, pady=2)

# Метка с датой
date_label = Label(date_control_frame, 
                text=current_date.strftime("%d.%m.%Y"), 
                fg='white', 
                bg='black', 
                font=('Arial', 14, 'bold'))
date_label.pack(side=LEFT, padx=10)

# Кнопка загрузки (оставляем в правом нижнем углу)
download_button = Button(root, 
                        text='Загрузить данные', 
                        bg='white', 
                        command=open_excel_files,
                        font=BUTTON_FONT)
download_button.place(relx=0.98, rely=0.95, anchor=SE)

# Параметры прямоугольника (добавьте в начало с другими параметрами)
rect_x1 = w - 625  # Левый верхний угол X
rect_y1 = h - 500  # Левый верхний угол Y
rect_x2 = w - 50  # Правый нижний угол X
rect_y2 = h - 175  # Правый нижний угол Y
rect_outline_color = "cyan"  # цвет обводки
rect_outline_width = 3  # Толщина обводки
rect_font = ("Arial", 14)  # Шрифт

# Создаем прямоугольник с разными координатами
status_rect = canvas.create_rectangle(
    rect_x1, rect_y1,
    rect_x2, rect_y2,
    outline=rect_outline_color,
    width=rect_outline_width,
    fill='black'  # Фон прямоугольника
)

# Создаем текстовый элемент внутри прямоугольника
status_text = canvas.create_text(
    (rect_x1 + rect_x2) / 2,  # Центр по X
    (rect_y1 + rect_y2) / 2,  # Центр по Y
    text="СТАТУС СИСТЕМЫ\n\nОжидание данных...",
    fill="white",
    font=rect_font,
    justify=CENTER,
    width=(rect_x2 - rect_x1) - 40,  # Ширина текста с отступами
    anchor="center"
)

# Функция для обновления текста
def set_status_message(message):
    """Устанавливает текст сообщения в прямоугольнике"""
    canvas.itemconfig(status_text, text=message)
    # Обновляем отображение
    canvas.update_idletasks()

# Примеры использования:
set_status_message("СИСТЕМА В РАБОТЕ\n\nТекущий статус: норма\nЗагрузка: 75%")
# set_status_message("ВНИМАНИЕ!\n\nОбнаружена ошибка\nКод: 45")
# set_status_message("РАБОТА ЗАВЕРШЕНА\n\nВсе процессы\nостановлены")



root.mainloop()

