from PIL import Image
import ctypes #Подключаем типы из С/С++
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta #изменение месяца pip install python-dateutil
import math
import numpy
import pandas as pd
import random
from tkinter import *
from tkinter.filedialog import askopenfilenames
from tkinter.messagebox import showinfo, showerror
from PIL import Image, ImageTk


# Глобальные переменные для моточасов из Excel
initial_to_hours = []
initial_kr_hours = []

# Читаем данные
current_date = datetime.now().date()
# Предыдущий день для расчета моточасов
previous_date_for_gtu = current_date

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
    filepaths = askopenfilenames(filetypes=[("Excel files", "*.xlsx")])

    if not filepaths:
        return  

    try:
        global energy_usage_data, gtu_data, gas_data, months, gas_prices
        global m_hours, m_to_hours, m_kr_hours  # Объявляем глобальными

        energy_path = filepaths[0] #Добавлена загрузка трех файлов
        gtu_path = filepaths[1]
        gas_path = filepaths[2]

        gtu_data = pd.read_excel(gtu_path)
        gas_data = pd.read_excel(gas_path, sheet_name='Лист1', header=None)

        # Обработка газовых цен
        last_col = gas_data.loc[2, 1:].last_valid_index()
        months = gas_data.loc[0, 1:last_col].to_numpy()
        gas_prices = gas_data.loc[2, 1:last_col].to_numpy()

        # Расчет моточасов только при загрузке файлов
        last_col_index = gtu_data.columns[-1]
        m_hours = gtu_data.loc[3:, last_col_index].dropna().to_numpy(dtype=float)
        m_to_hours = numpy.where(m_hours > 1500, m_hours % 1500, m_hours)
        m_kr_hours = numpy.where(m_hours > 10000, m_hours % 10000, m_hours)
        m_hours = numpy.round(m_hours, 3)

        global initial_to_hours, initial_kr_hours, gtes

        initial_to_hours = m_to_hours.copy()
        initial_kr_hours = m_kr_hours.copy()

        # Создаём список объектов GTU по числу данных
        gtes = [GTU(i) for i in range(len(m_hours))]

        # Присваиваем каждому GTU его начальные данные
        for idx, gtu in enumerate(gtes):
            gtu.to = initial_to_hours[idx]
            gtu.kr = initial_kr_hours[idx]

        print("Файлы успешно загружены!")
        showinfo("Успех!", "Файлы успешно загружены!")

        set_status_message(f"СИСТЕМА В РАБОТЕ\n\n{price_calc()}")
        boilers_initialization()
        gtu_initialization()

    except Exception as e:
        showerror("Ошибка!", f"Ошибка при загрузке файлов:\n{e}")



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

LastButton = None

def next_date():
    global current_date, previous_date_for_gtu, LastButton
    current_date += timedelta(days=1)
    update_label()
    set_status_message(f"СИСТЕМА В РАБОТЕ\n\n{price_calc()}")
    boilers_initialization()
    gtu_initialization()
    previous_date_for_gtu = current_date
    LastButton = "next_date"

def previous_date():
    global current_date, previous_date_for_gtu, LastButton
    current_date -= timedelta(days=1)
    update_label()
    set_status_message(f"СИСТЕМА В РАБОТЕ\n\n{price_calc()}")
    boilers_initialization()
    gtu_initialization()
    previous_date_for_gtu = current_date
    LastButton = "previous_date"

def next_month():
    global current_date, previous_date_for_gtu, LastButton
    current_date += relativedelta(months=1)
    update_label()
    set_status_message(f"СИСТЕМА В РАБОТЕ\n\n{price_calc()}")
    boilers_initialization()
    gtu_initialization()
    previous_date_for_gtu = current_date
    LastButton = "next_month"

def previous_month():
    global current_date, previous_date_for_gtu, LastButton
    current_date -= relativedelta(months=1)
    update_label()
    set_status_message(f"СИСТЕМА В РАБОТЕ\n\n{price_calc()}")
    boilers_initialization()
    gtu_initialization()
    previous_date_for_gtu = current_date
    LastButton = "previous_month"

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

last_5_temps = [None, None, None, None, None]   
def heat_from_temp(temp):
    """
    Функция потребности тепла в зависимости от отрицательной температуры воздуха 
    temp - температура воздуха

    Функция должна срабатывать, когда среднесуточная температура 
    на улице держится ниже +8 °C в течение 5 дней подряд
    """
    heat_need = 0
    global last_5_temps

    last_5_temps.append(temp)

    if len(last_5_temps) > 5:
        last_5_temps.pop(0)

    if None not in last_5_temps and all(t < 8 for t in last_5_temps):
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


class GTU:
    def __init__(self, n):
        self.n = n # номер ГТУ
        self.power = 16 # номинальная мощность
        self.load = 1 # уровень загрузки (о.е.)
        self.to = 1500 # моточасы до ТО
        self.kr = 10000 # моточасы до КР
        self.state = 0 # состояние 0-выкл/1-вкл/2-ТО или КР
        self.service_time = 0 # время сервисного обслуживания: 14 дней для ТО и 30 дней для КР
    
    def stop_to(self):
        self.state = 2
        self.service_time = 14
        self.to = 1500
        
    def stop_kr(self):
        self.state = 2
        self.service_time = 30
        self.to = 1500
        self.kr = 10000
        
    def stop_n(self):
        self.state = 0
        self.to = self.to - 2.5
        self.kr = self.kr - 2.5
        
    def start_n(self):
        self.state = 1
        self.to = self.to - 2.5
        self.kr = self.kr - 2.5
    
    def __str__(self):
        return f'''
        номер ГТУ {self.n}
        номинальная мощность {self.power}
        уровень загрузки (о.е.) {self.load}
        моточасы до ТО {self.to}
        моточасы до КР {self.kr}
        состояние вкл/выкл {self.state}
        '''
    
def hourly_production(load):
    x = load
    y = -1.6667*x**3+3.3333*x*x-1.1833*x+0.5167 # кубическая регрессия для нахождения отношения мч/ч
    
    return y

def get_power_loss(temp, season):
    base_node_voltage = 11 # напряжение базисного узла, кВ
    rated_voltage = 10 # номинальное напряжение сети, кВ
    
    node_type = ['base'] # тип узла
    number_of_circuits = [] # количество цепей, шт.
    
    for i in range(32):
        node_type.append('load')
        number_of_circuits.append(2)
        
    r0 = 0.245/(1+0.00403*(20-temp)) # скорректированное на текущую температуру погонное сопротивление АС-120/19
    x0 = 0.38
    
    line_lengths = [0.5, 3, 3.5, 4, 100, 1, 2, 3, 3.3, 4, 4.5, 5, 5.2, 5.7, 6, 6.5, 7, 7.5, 7.8, 8, 8.5, 9, 9.3,
                   9.7, 17, 18, 20, 22, 23, 24, 25, 0.3] # длины линий
    
    linear_active_resistance = [ll*r0 for ll in line_lengths] # активное сопротивление ветвей, Ом
    linear_reactive_resistance = [ll*x0 for ll in line_lengths] # реактивное сопротивление ветвей, Ом
    
    starting_point = [0 for i in range(32)] # номер узла, где ветвь начинается
    end_point = [i for i in range(1, 33)] # номер узла, где ветвь заканчивается
    
    # исходные данные узлов: нагрезка <0; источник >0
    power = [30, 9, 2, 3, 10, 0.7, 0.8, 0.5, 0.9, 1, 0.9, 0.5, 1, 1.3, 1, 0.8, 0.6, 0.8, 1, 1, 0.7, 1, 0.8, 1,
        1.1, 1, 2.2, 1.4, 1.2, 1.3, 1.4, 22] # нагрузки узлов
    
    sn_summer = [90, 80, 100, 100, 100]
    for i in range(26):
        sn_summer.append(50)
    sn_summer.append(70)
    
    sn_winter = [95, 90]
    for i in range(29):
        sn_winter.append(100)
    sn_winter.append(55)
    
    if season == "summer":
        sn = sn_summer
    else:
        sn = sn_winter
    
    s = [] # полная мощность узлов, МВА
    for i, pow in enumerate(power):
        p = pow * sn[i] / 100
        q = p * math.tan(math.acos(0.97))
        s.append(-complex(p, q))
    
    number_of_nodes = len(s)+1 # количество узлов + 1 базисный
    number_of_branches = len(starting_point) # количество ветвей
    base_node_number = node_type.index('base') # номер базисного узла
    
    u=[base_node_voltage+0*1j for i in range(number_of_nodes-1)] # начальные приближения напряжений
    
    # составление первой матрицы инциденций
    M_sum = [[0 for j in range(number_of_branches)] for i in range(number_of_nodes)]
    for i in range(number_of_branches):
        M_sum[starting_point[i]][i] = 1
        M_sum[end_point[i]][i] = -1
        
    # составление матрицы М, не содержащей базисного угла (удалена 0 строка)
    M = M_sum
    M = numpy.delete(M, base_node_number, axis=0)
    
    # формирование матрицы сопротивлений ветвей (диагональная)
    z_branches = [[0 for j in range(number_of_branches)] for i in range(number_of_branches)]
    for i in range(number_of_branches):
        z_branches[i][i]=linear_active_resistance[i]+linear_reactive_resistance[i]*1j
        
    # формирование матрицы узловых проводимостей
    y_nodes = M.dot(numpy.linalg.inv(z_branches)).dot(M.transpose())
    
    # матрица сопротивлений узлов
    z_nodes = numpy.linalg.inv(y_nodes)
    
    # формирование матрицы узловых токов
    node_current = []
    for i in range(number_of_nodes-1):
        node_current.append(s[i].conjugate()/rated_voltage.conjugate())
        
    # расчет напряжений в узлах
    result_u = u+z_nodes.dot(node_current)
    result_u = numpy.insert(result_u, base_node_number, base_node_voltage)
    result_abs_u = abs(result_u)
    
    # расчет токов в линиях
    result_i = numpy.linalg.inv(z_branches).dot((numpy.transpose(M_sum)).dot(result_u))/3**0.5
    abs_result_i = abs(result_i)
    
    # расчет потерь в линиях
    dp = []
    for i in range(len(linear_active_resistance)):
        I = abs_result_i[i]
        dp.append((I)**2*3*linear_active_resistance[i])
    
    return sum(dp)

def month_delta(start_date, end_date):
    return (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)

def gtu_initialization():
    global m_to_hours, m_kr_hours, previous_date_for_gtu
    time_delta_day = (current_date - previous_date_for_gtu).days
    time_delta_month = month_delta(previous_date_for_gtu, current_date)

    current_datetime = current_date # текущая дата
    custom_datetime_1 = 6
    custom_datetime_2 = 10
    current_season = None
    if 6<= current_datetime.month <10:
        current_season = 'summer'
    else:
        current_season = 'winter'

    # определение мощности потребления
    p_sum = None
    if current_season == 'summer':
        p_sum = 77.6
    else:
        p_sum = 89.7
    p_sum += get_power_loss(10, current_season)

    n_gtu = math.ceil(p_sum / 16) # определение числа необходимых ГТУ
    actual_loading = round(p_sum / n_gtu / 16, 2) # определение фактической загрузки ГТУ
    hp = hourly_production(actual_loading) # определение отношения мч/ч
    engine_hpd = hp * 24 # наработка за сутки при данной нагрузке

    # отключение ГТУ по состоянию
    for gtu in gtes:
        if gtu.state == 1:
            if gtu.kr-engine_hpd-2.5 <= 0:
                gtu.stop_kr()
                # плюс к затратам за КР
            elif gtu.to-engine_hpd-2.5 <= 0:
                gtu.stop_to()
                # плюс к затратам за ТО
            else:
                continue

    # отключение ГТУ по количеству n_gtu
    gtes.sort(key=lambda x: x.kr)
    n = 0
    for gtu in gtes:
        if gtu.state == 0 and n < n_gtu:
            if n < n_gtu:
                n += 1
            else:
                gtu.stop_n()
                
    # запуск ГТУ по количеству n_gtu
    n = 0
    for gtu in gtes:
        if gtu.state == 0:
            if n < n_gtu:
                gtu.start_n()
                n += 1

    # обновление состояний ГТУ по прошествии дня
    if (LastButton == "next_date" or LastButton == "previous_date"):
        for gtu in gtes:
            
            # Для рабочей ГТУ
            if gtu.state == 1:
                gtu.to -= engine_hpd * time_delta_day
                gtu.kr -= engine_hpd * time_delta_day
                if gtu.to < 0:
                    gtu.to = 0
                if gtu.kr < 0:
                    gtu.kr = 0

            #Считаем дни ремонта для ГТУ на обслуживании
            elif gtu.state == 2:
                gtu.service_time -= abs(time_delta_day)
                if gtu.service_time == 0:
                    gtu.state = 0
            else:
                continue
    elif (LastButton == "next_month" or LastButton == "previous_month"):
        for gtu in gtes:
            
            # Для рабочей ГТУ
            if gtu.state == 1:
                gtu.to -= engine_hpd * time_delta_month
                gtu.kr -= engine_hpd * time_delta_month
                if gtu.to < 0:
                    gtu.to = 0
                if gtu.kr < 0:
                    gtu.kr = 0

            #Считаем дни ремонта для ГТУ на обслуживании
            elif gtu.state == 2:
                gtu.service_time -= abs(time_delta_month)
                if gtu.service_time == 0:
                    gtu.state = 0
            else:
                continue

    for gtu in gtes:
        print(gtu)
        GTU_info(gtu.n + 1, gtu.power, gtu.load, f'{gtu.to:.3f}', f'{gtu.kr:.3f}', gtu.state)
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
    text_x += (w * 0.002)
    text_y += (w * 0.001)
    

    img_x, img_y = GTU_dict[num]["coords"]
    
 
    if state == 1:
        canvas.create_image(img_x, img_y, image=gtu_on, anchor="nw", tags=f"gtu_{num}")
    elif state == 0:
        canvas.create_image(img_x, img_y, image=gtu_off, anchor="nw", tags=f"gtu_{num}")
    elif state == 2:
        canvas.create_image(img_x, img_y, image=gtu_repair, anchor="nw", tags=f"gtu_{num}")
    
    lines = [
        f"Номер ГТУ: {num}",
        f"Номинальная W: {wt}Мвт",
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
            font=("Arial", int(h*0.009)),
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
    text_x += (w * 0.002)
    text_y += (w * 0.001)
    
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
            font=("Arial", int(h*0.009)),
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

