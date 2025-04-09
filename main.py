from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showinfo, showerror
from PIL import Image, ImageTk 
import pandas as pq # библиотека для excel (pip install pandas openpyxl xlrd)
import ctypes #Подключаем типы из С/С++
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta #изменение месяца pip install python-dateutil
#from boilers import UtilizationBoiler, heat_from_temp, heat_load_distribution, heat_cost

# Чтение файла excel 
exel_1 = pq.read_excel("Excel/1_Данные_по_потреблению_электроэнергии.xlsx")
exel_2 = pq.read_excel("Excel/2_Наработка_ГТЭС.xlsx")
exel_3 = pq.read_excel("Excel/3_Стоимость_СОГ.xlsx")

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

current_date = datetime.now().date()

def fullscreen(event):
    global is_fullscreen
    is_fullscreen = not is_fullscreen
    root.attributes('-fullscreen', is_fullscreen)

def open_file():
    filepath = askopenfilename()
    if filepath != "":
        with open(filepath, 'r', encoding='utf8') as file:
            try:
                print(filepath)
                showinfo("Успех!", "Файл успешно загружен.")
            except Exception:
                showerror("Ошибка!", "Ошибка при чтении файла.")

# Загрузка и масштабирование изображения
def load_scaled_image(path, size):
    img = Image.open(path)
    img = img.resize((int(size), int(size)), Image.LANCZOS) 
    return ImageTk.PhotoImage(img)

def update_label():
    label.config(text=current_date.strftime("%d.%m.%Y"), fg='white', bg='black', font=('Arial', 35))

def next_date():
    global current_date
    current_date += timedelta(days=1)
    update_label()

def next_month():
    global current_date
    current_date += relativedelta(months=1)
    update_label()

def previous_date():
    global current_date
    current_date -= timedelta(days=1)
    update_label()

def previous_month():
    global current_date
    current_date -= relativedelta(months=1)
    update_label()

###################################################################################

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
     
# Создаем 9 изображений ГТУ
GTU1 = canvas.create_image(xG, yG, image=gtu_on, anchor="nw")
GTU2 = canvas.create_image(xG + (sizeG + marginG)*1, yG, image=gtu_on, anchor="nw")
GTU3 = canvas.create_image(xG + (sizeG + marginG)*2, yG, image=gtu_on, anchor="nw")
GTU4 = canvas.create_image(xG + (sizeG + marginG)*3, yG, image=gtu_on, anchor="nw")
GTU5 = canvas.create_image(xG + (sizeG + marginG)*4, yG, image=gtu_on, anchor="nw")
GTU6 = canvas.create_image(xG + (sizeG + marginG)*5, yG, image=gtu_on, anchor="nw")
GTU7 = canvas.create_image(xG + (sizeG + marginG)*6, yG, image=gtu_on, anchor="nw")
GTU8 = canvas.create_image(xG + (sizeG + marginG)*7, yG, image=gtu_on, anchor="nw")
GTU9 = canvas.create_image(xG + (sizeG + marginG)*8, yG, image=gtu_on, anchor="nw")

# Худ для ГТУ
colorG = "green" #Настройка цвета
widthG = 3 #Настройка толщины обводки
shiftG = w * 0.1 #Настройка сдвига худа (по умолчанию находится на месте самого ГТУ)

GTU_hud1 = canvas.create_rectangle(xG, yG + shiftG, xG + sizeG, yG + shiftG + sizeG, outline=colorG, width=widthG)
GTU_hud2 = canvas.create_rectangle(xG + (sizeG + marginG)*1, yG + shiftG, xG + sizeG + (sizeG + marginG)*1, yG + shiftG + sizeG, outline=colorG, width=widthG)
GTU_hud3 = canvas.create_rectangle(xG + (sizeG + marginG)*2, yG + shiftG, xG + sizeG + (sizeG + marginG)*2, yG + shiftG + sizeG, outline=colorG, width=widthG)
GTU_hud4 = canvas.create_rectangle(xG + (sizeG + marginG)*3, yG + shiftG, xG + sizeG + (sizeG + marginG)*3, yG + shiftG + sizeG, outline=colorG, width=widthG)
GTU_hud5 = canvas.create_rectangle(xG + (sizeG + marginG)*4, yG + shiftG, xG + sizeG + (sizeG + marginG)*4, yG + shiftG + sizeG, outline=colorG, width=widthG)
GTU_hud6 = canvas.create_rectangle(xG + (sizeG + marginG)*5, yG + shiftG, xG + sizeG + (sizeG + marginG)*5, yG + shiftG + sizeG, outline=colorG, width=widthG)
GTU_hud7 = canvas.create_rectangle(xG + (sizeG + marginG)*6, yG + shiftG, xG + sizeG + (sizeG + marginG)*6, yG + shiftG + sizeG, outline=colorG, width=widthG)
GTU_hud8 = canvas.create_rectangle(xG + (sizeG + marginG)*7, yG + shiftG, xG + sizeG + (sizeG + marginG)*7, yG + shiftG + sizeG, outline=colorG, width=widthG)
GTU_hud9 = canvas.create_rectangle(xG + (sizeG + marginG)*8, yG + shiftG, xG + sizeG + (sizeG + marginG)*8, yG + shiftG + sizeG, outline=colorG, width=widthG)

center_x = xG + (w * 0.005)
center_y = yG + shiftG + (w * 0.003)

# Создаем текст по центру первого прямоугольника
canvas.create_text(
    center_x, 
    center_y,
    text="номер ГТУ: \n\
номинальная W: \n\
уровень загрузки: \n\
моточасы до ТО: \n\
моточасы до КР: \n\
состояние:",  # Ваш текст
    anchor="nw",        # Центрирование относительно точки
    fill="white",           # Цвет текста
    font=("Arial", int(w*0.007))      # Шрифт и размер (опционально)
)

# Котлы
marginB = w * 0.08  # Отступы
sizeB = w * 0.09  # Размер
num_blr = 6 # Кол-во котлов
widthB = num_blr * sizeB + (num_blr - 1) * marginB #Расчитываем ширину

xB = (w - widthB) / 2       # Начальная координата X
yB = w * 0.26     # Начальная координата Y

boiler_on = load_scaled_image("img/Boiler_on.png", sizeG)

# Создаем 6 изображений Котлов
BLR1 = canvas.create_image(xB, yB, image=boiler_on, anchor="nw")
BLR2 = canvas.create_image(xB + (sizeB + marginB)*1, yB, image=boiler_on, anchor="nw")
BLR3 = canvas.create_image(xB + (sizeB + marginB)*2, yB, image=boiler_on, anchor="nw")
BLR4 = canvas.create_image(xB + (sizeB + marginB)*3, yB, image=boiler_on, anchor="nw")
BLR5 = canvas.create_image(xB + (sizeB + marginB)*4, yB, image=boiler_on, anchor="nw")
BLR6 = canvas.create_image(xB + (sizeB + marginB)*5, yB, image=boiler_on, anchor="nw")

# Худ для Котлов
colorB = "green" #Настройка цвета
widthB = 3 #Настройка толщины обводки
shiftB = w * 0.1 #Настройка сдвига худа (по умолчанию находится на месте самого ГТУ)

BLR_hud1 = canvas.create_rectangle(xB, yB + shiftB, xB + sizeB, yB + shiftB + sizeB, outline=colorB, width=widthB)
BLR_hud2 = canvas.create_rectangle(xB + (sizeB + marginB)*1, yB + shiftB, xB + sizeB + (sizeB + marginB)*1, yB + shiftB + sizeB, outline=colorB, width=widthB)
BLR_hud3 = canvas.create_rectangle(xB + (sizeB + marginB)*2, yB + shiftB, xB + sizeB + (sizeB + marginB)*2, yB + shiftB + sizeB, outline=colorB, width=widthB)
BLR_hud4 = canvas.create_rectangle(xB + (sizeB + marginB)*3, yB + shiftB, xB + sizeB + (sizeB + marginB)*3, yB + shiftB + sizeB, outline=colorB, width=widthB)
BLR_hud5 = canvas.create_rectangle(xB + (sizeB + marginB)*4, yB + shiftB, xB + sizeB + (sizeB + marginB)*4, yB + shiftB + sizeB, outline=colorB, width=widthB)
BLR_hud6 = canvas.create_rectangle(xB + (sizeB + marginB)*5, yB + shiftB, xB + sizeB + (sizeB + marginB)*5, yB + shiftB + sizeB, outline=colorB, width=widthB)

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
                        command=open_file,
                        font=BUTTON_FONT)
download_button.place(relx=0.98, rely=0.95, anchor=SE)

# Функция обновления даты (модифицированная)
def update_label():
    date_label.config(text=current_date.strftime("%d.%m.%Y"))

root.mainloop()