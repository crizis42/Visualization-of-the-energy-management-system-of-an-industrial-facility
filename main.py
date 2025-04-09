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
        set_status_message(f"СИСТЕМА В РАБОТЕ\n\n{price_calc()}")
        boilers_initialization()


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
            price = gas_prices[current_month - 1]/1000
    elif current_year == 2025:
        price = gas_prices[-1]/1000
    elif current_year == 2026:
        price = gas_prices[-1]/1000
    else:
        price = 0  # Нет данных на этот год

    # Вывод в терминал
    if price != 0:
        return(f'Стоимость газа на {current_day}.{current_month}.{current_year} = {price:.3f} руб/тыс.м³')
    else:
        return(f'Нет данных для расчета стоимости газа за {current_month}.{current_year}')

    

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
    set_status_message(f"СИСТЕМА В РАБОТЕ\n\n{price_calc()}")
    boilers_initialization()

def previous_date():
    global current_date
    current_date -= timedelta(days=1)
    update_label()
    set_status_message(f"СИСТЕМА В РАБОТЕ\n\n{price_calc()}")
    boilers_initialization()

def next_month():
    global current_date
    current_date += relativedelta(months=1)
    update_label()
    set_status_message(f"СИСТЕМА В РАБОТЕ\n\n{price_calc()}")
    boilers_initialization()

def previous_month():
    global current_date
    current_date -= relativedelta(months=1)
    update_label()
    set_status_message(f"СИСТЕМА В РАБОТЕ\n\n{price_calc()}")
    boilers_initialization()

class UtilizationBoiler:
    """Котел утилизатор КВ-ГМ-3,15-95.

    
    Внутренние атрибуты:
    num_boiler - номер утилизатора 
    pwr - номинальная мощность, Гкал
    kpd - КПД
    load - уровень загрузки, %
    status - True/False (вкл/выкл)
    """
    
    def __init__(self, num_boiler):
        self.num = num_boiler
        self.pwr = 2.7
        self.kpd = 0.935
        self.load = 0
        self.status = False

    def start(self):
        """Запуск котла"""
        if not self.status:
            self.status = True
            return f'Котел-утилизатор {self.num} запущен.'
        return f'Котел-утилизатор {self.num} уже запущен.'

    def stop(self):
        """Останов котла"""
        if self.status:
            self.status = False
            return f'Котел-утилизатор {self.num} остановлен.'
            
        return f'Котел-утилизатор {self.num} уже остановлен.'

    def load_b(self, load_boil):
        """Изменение загрузки котла"""
        self.load = load_boil
        
        return f'Уровень загрузки котла {self.num}: {self.load} %'

    
    def heat_otpt(self):
        """генерируемая тепловая мощность от процента загрузки котла, Гкал

        load - загрузка котла, % """

        if self.load > 100:
            self.load = 100
        elif self.load < 0:
            self.load = 0
            
        heat = 0
        if self.status:
            heat = float(format(
                                (self.pwr * self.load/100), '.3f'
                                )
                        )
        return heat
        
    def gas_cons(self):
        """Потребление газа котлом, м3/ч"""
        cons = 0
        gas_cal_val = 0.01075 # теплотворная способность газа, Гкал/м3
        
        if self.status:
            cons = float(format(
                                ((self.heat_otpt()/gas_cal_val)/self.kpd), '.3f'
                                )
                        )
        return cons

    def __str__(self):
        return f'''Номер котла: {self.num}
        Номинальная мощность: {self.pwr}
        Уровень загрузки: {self.load} % / {self.heat_otpt()} Гкал
        Состояние вкл/выкл: {self.status}
        '''
    
def heat_from_temp(temp):
    """
    Функция потребности тепла в зависимости от отрицательной температуры воздуха 
    temp - температура воздуха

    Функция должна срабатывать, когда среднесуточная температура 
    на улице держится ниже +8 °C в течение 5 дней подряд
    """
    heat_need = 0
    
    if temp < 8:
        # кубическая регрессия от x: 0 -10 -24 -38 -48; y: 1.126 2.345 5.63 8.914 11.26;
        heat_need = float(format(
                                (0.00006180 * temp ** 3 + 0.00559107 * temp ** 2 - 0.08512969 * temp + 1.09309420), '.3f'
                                )
                        )
    
    return heat_need

def heat_load_distribution(ht_fr_dist):
    """Функция распределяет выработку тепла между работающими котлами.
    
    quant_boiler - количество работающих котлов
    ht_fr_dist - тепло, подлежащее распределению (из выхода ф-ии heat_from_temp)"""

    quant_boiler = 6
    load = float(format(
                        (((ht_fr_dist / quant_boiler) / 2.7) * 100), '.3f'
                        )
                )

    if load < 45.0: 
        while load < 45.0:
            quant_boiler = quant_boiler - 1
            
            if quant_boiler != 1:
                load = float(format(
                                    (((ht_fr_dist / quant_boiler) / 2.7) * 100), '.3f'
                                    )
                            )
            else:
                break

    if ht_fr_dist == 0:
        load = 0
        quant_boiler = 0
        
    return load, quant_boiler

def heat_cost(boilers):
    """Функция расчета стоимости газа, руб/ч"""
    global price

    try:
        # Проверяем, рассчитана ли цена
        if price is None:
            raise ValueError("Ошибка: цена на газ не определена!")

        gas_cons = [boiler.gas_cons() for boiler in boilers]
        cost = sum(gas_cons) * price
        return cost

    except ValueError as e:
        print(e)
        return 0  # Возвращаем 0 если цена не определена

    except Exception as e:
        print(f"Неизвестная ошибка при расчете стоимости газа: {e}")
        return 0

def temp_of_month():
    temp = [-28.1, -27.3, -21.6, -14.9, -5.4, 6.1, 13.7, 10.8, 3.9, -8.3, -20.5, -24.7]
    return temp[current_date.month-1]

def boilers_initialization():
    # Инициализация котлов
    boilers = [UtilizationBoiler(i) for i in range(6)]
    

    temp = temp_of_month()

    heat_need = heat_from_temp(temp) # Потребность в тепле
    print(f'Потребность в тепле: {heat_need} Гкал/ч')

    load_val = heat_load_distribution( heat_need )[0]
    print(f'Загрузка одного котла: {load_val} %')

    num_boilers_must_on = heat_load_distribution( heat_need )[1] # Число котлов, которые должны быть запущены
    print(f'Должно быть запущено котлов: {num_boilers_must_on}')

    # Вкл нужного количества котлов
    n_boil_on = 6 - num_boilers_must_on

    for boiler in boilers:
        if boiler.num > n_boil_on - 1:
            print(boiler.start())
        if boiler.num < n_boil_on - 1:
            if not boiler.status:
                print(boiler.stop())

    # Передача нужного значения загрузки котлу
    for boiler in boilers:
        if boiler.status:
            load = boiler.load_b(load_val)
            print(load)

    print(f'Стоимость газа: {heat_cost(boilers)} руб/ч')

    # Вывод информации о каждом котле после расчета
    for boiler in boilers:
        print(boiler)
        BLR_info(boiler.num + 1, boiler.load, boiler.pwr, boiler.status)



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
def GTU_info(num, wt, prcnt, hTO, hKR, state):
    
    canvas.delete(f"gtu_{num}")  # Общий тег для всех элементов
   
    text_x, text_y = GTU_huds[num]["coords"]
    text_x += (w * 0.005)
    text_y += (w * 0.003)
    

    img_x, img_y = GTU_dict[num]["coords"]
    
 
    if state == "on":
        canvas.create_image(img_x, img_y, image=gtu_on, anchor="nw", tags=f"gtu_{num}")
    elif state == "off":
        canvas.create_image(img_x, img_y, image=gtu_off, anchor="nw", tags=f"gtu_{num}")
    elif state == "repair":
        canvas.create_image(img_x, img_y, image=gtu_repair, anchor="nw", tags=f"gtu_{num}")
    
    lines = [
        f"Номер ГТУ: {num}",
        f"Номинальная W: {wt}Квт",
        f"Уровень загрузки: {prcnt}%",
        f"Моточасы до ТО: {hTO}ч",
        f"Моточасы до КР: {hKR}ч",
    ]
    
    for i, line in enumerate(lines):
        canvas.create_text(
            text_x,
            text_y + i * int(w * 0.015),
            text=line,
            anchor="nw",
            fill="white",
            font=("Arial", int(h*0.01)),
            tags=f"gtu_{num}" 
        )

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

    canvas.delete(f"blr_{num}")

    img_x, img_y = BLR_dict[num]["coords"]
    
    # Координаты для текста
    text_x, text_y = BLR_huds[num]["coords"]
    text_x += (w * 0.005)
    text_y += (w * 0.003)
    
    if state:  # True или "on"
        canvas.create_image(img_x, img_y, image=boiler_on, anchor="nw", tags=f"blr_{num}")
    else:  # False или "off"
        canvas.create_image(img_x, img_y, image=boiler_off, anchor="nw", tags=f"blr_{num}")

    lines = [
        f"Номер котла: {num}",
        f"Уровень загрузки: {prcnt}%",
        f"Мощность: {pwr}Гкал"
    ]
    
    for i, line in enumerate(lines):
        canvas.create_text(
            text_x,
            text_y + i * int(w * 0.015),
            text=line,
            anchor="nw",
            fill="white",
            font=("Arial", int(h*0.01)),
            tags=f"blr_{num}"  # Тот же тег
        )


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
rect_x1, rect_y1 = BLR_dict[6]["coords"]
rect_y1 += (h * 0.037)
rect_x1 = xG + (sizeG + marginG)*6

rect_x2 = xG + sizeG + (sizeG + marginG)*8
rect_y2 = yB + shiftB + sizeB

rect_outline_color = "#f0f0f0"  # цвет обводки
rect_outline_width = 3  # Толщина обводки
rect_font = ("Arial", 20)  # Шрифт

# Создаем прямоугольник с разными координатами
status_rect = canvas.create_rectangle(
    rect_x1, rect_y1,
    rect_x2, rect_y2,
    outline=rect_outline_color,
    width=rect_outline_width,
)

text_padding_x = (w * 0.005)  # Горизонтальный отступ
text_padding_y = (w * 0.004)  # Вертикальный отступ

# Создаем текстовый элемент в левом верхнем углу прямоугольника
status_text = canvas.create_text(
    rect_x1 + text_padding_x,  # X: левый край + отступ
    rect_y1 + text_padding_y,  # Y: верхний край + отступ
    text="СТАТУС СИСТЕМЫ\n\nОжидание данных...",
    fill="white",
    font=rect_font,
    justify=LEFT,  # Выравнивание по левому краю
    width=(rect_x2 - rect_x1) - 2*text_padding_x,  # Ширина с учетом отступов
    anchor="nw"  # Привязка к северо-западному углу (левому верхнему)
)

# Функция для обновления текста (оставляем без изменений)
def set_status_message(message):
    """Устанавливает текст сообщения в прямоугольнике"""
    canvas.itemconfig(status_text, text=message)
    canvas.update_idletasks()

# Примеры использования:

# set_status_message("ВНИМАНИЕ!\n\nОбнаружена ошибка\nКод: 45")
# set_status_message("РАБОТА ЗАВЕРШЕНА\n\nВсе процессы\nостановлены")



root.mainloop()

