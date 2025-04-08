from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showinfo, showerror


root = Tk()
 
root.title('Визуализация системы')
root['bg'] = 'black'

w = root.winfo_screenwidth()
h = root.winfo_screenheight()

root.geometry(f'{w}x{h}+0+0')


def fullscreen_on(event):
    root.attributes('-fullscreen', True)

def fullscreen_off(event):
    root.attributes('-fullscreen', False)

def open_file():
    filepath = askopenfilename()
    if filepath != "":
        with open(filepath, 'r', encoding='utf8') as file:
            try:
                print(filepath)
                showinfo("Успех!", "Файл успешно загружен.")
            except Exception:
                showerror("Ошибка!", "Ошибка при чтении файла.")


root.bind('<f>', fullscreen_on)
root.bind('<Escape>', fullscreen_off)

# Создаем холст (Canvas) для рисования
canvas = Canvas(root, bg='black', highlightthickness=0)
canvas.place(x=0, y=0, width=w, height=h)  # Растягиваем на весь экран

# Установки ГТУ
marginG = w * 0.02  # Отступы
sizeG = w * 0.09  # Размер
xG = 10       # Начальная координата X
yG = 10       # Начальная координата Y

canvas.create_rectangle(xG, yG, xG + sizeG, yG + sizeG, fill='blue', outline='white')
canvas.create_rectangle(xG + (sizeG + marginG)*1, yG, xG + sizeG + (sizeG + marginG)*1, yG + sizeG, fill='blue', outline='white')
canvas.create_rectangle(xG + (sizeG + marginG)*2, yG, xG + sizeG + (sizeG + marginG)*2, yG + sizeG, fill='blue', outline='white')
canvas.create_rectangle(xG + (sizeG + marginG)*3, yG, xG + sizeG + (sizeG + marginG)*3, yG + sizeG, fill='blue', outline='white')
canvas.create_rectangle(xG + (sizeG + marginG)*4, yG, xG + sizeG + (sizeG + marginG)*4, yG + sizeG, fill='blue', outline='white')
canvas.create_rectangle(xG + (sizeG + marginG)*5, yG, xG + sizeG + (sizeG + marginG)*5, yG + sizeG, fill='blue', outline='white')
canvas.create_rectangle(xG + (sizeG + marginG)*6, yG, xG + sizeG + (sizeG + marginG)*6, yG + sizeG, fill='blue', outline='white')
canvas.create_rectangle(xG + (sizeG + marginG)*7, yG, xG + sizeG + (sizeG + marginG)*7, yG + sizeG, fill='blue', outline='white')
canvas.create_rectangle(xG + (sizeG + marginG)*8, yG, xG + sizeG + (sizeG + marginG)*8, yG + sizeG, fill='blue', outline='white')

marginB = w * 0.02  # Отступы
sizeB = w * 0.09  # Размер
xB = 10       # Начальная координата X
yB = 250       # Начальная координата Y

canvas.create_rectangle(xB, yB, xB + sizeB, yB + sizeB, fill='blue', outline='white')
canvas.create_rectangle(xB + (sizeB + marginB)*1, yB, xB + sizeB + (sizeB + marginB)*1, yB + sizeB, fill='blue', outline='white')
canvas.create_rectangle(xB + (sizeB + marginB)*2, yB, xB + sizeB + (sizeB + marginB)*2, yB + sizeB, fill='blue', outline='white')
canvas.create_rectangle(xB + (sizeB + marginB)*3, yB, xB + sizeB + (sizeB + marginB)*3, yB + sizeB, fill='blue', outline='white')
canvas.create_rectangle(xB + (sizeB + marginB)*4, yB, xB + sizeB + (sizeB + marginB)*4, yB + sizeB, fill='blue', outline='white')
canvas.create_rectangle(xB + (sizeB + marginB)*5, yB, xB + sizeB + (sizeB + marginB)*5, yB + sizeB, fill='blue', outline='white')





download_button = Button(root, text='Загрузить данные', bg='white', command=open_file)
download_button.place(relx=0.95, rely=0.95, anchor=SE) #использовал rely relx
root.mainloop()