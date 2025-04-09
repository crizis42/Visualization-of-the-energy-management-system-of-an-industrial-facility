from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showinfo, showerror
from PIL import Image, ImageTk

is_fullscreen = False
root = Tk()
 
root.title('Визуализация системы')
root['bg'] = 'black'

w = root.winfo_screenwidth()
h = root.winfo_screenheight()

root.geometry(f'{w}x{h}+0+0')


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

####################################################################################

root.bind('<F11>', fullscreen)

# Создаем холст (Canvas) для рисования
canvas = Canvas(root, bg='black', highlightthickness=0)
canvas.place(x=0, y=0, width=w, height=h)  # Растягиваем на весь экран

# Установки ГТУ
marginG = w * 0.02  # Отступы
sizeG = w * 0.09  # Размер
xG = 10       # Начальная координата X
yG = 10       # Начальная координата Y

gtu_on = load_scaled_image("GTU_on.png", sizeG)

# Создаем 9 изображений ГТУ
img1 = canvas.create_image(xG, yG, image=gtu_on, anchor="nw")
img2 = canvas.create_image(xG + (sizeG + marginG)*1, yG, image=gtu_on, anchor="nw")
img3 = canvas.create_image(xG + (sizeG + marginG)*2, yG, image=gtu_on, anchor="nw")
img4 = canvas.create_image(xG + (sizeG + marginG)*3, yG, image=gtu_on, anchor="nw")
img5 = canvas.create_image(xG + (sizeG + marginG)*4, yG, image=gtu_on, anchor="nw")
img6 = canvas.create_image(xG + (sizeG + marginG)*5, yG, image=gtu_on, anchor="nw")
img7 = canvas.create_image(xG + (sizeG + marginG)*6, yG, image=gtu_on, anchor="nw")
img8 = canvas.create_image(xG + (sizeG + marginG)*7, yG, image=gtu_on, anchor="nw")
img9 = canvas.create_image(xG + (sizeG + marginG)*8, yG, image=gtu_on, anchor="nw")

marginB = w * 0.08  # Отступы
sizeB = w * 0.09  # Размер
xB = 10       # Начальная координата X
yB = 400       # Начальная координата Y

boiler_on = load_scaled_image("boiler_on.png", sizeG)

# Создаем 6 изображений Котлов
img1 = canvas.create_image(xB, yB, image=boiler_on, anchor="nw")
img2 = canvas.create_image(xB + (sizeB + marginB)*1, yB, image=boiler_on, anchor="nw")
img3 = canvas.create_image(xB + (sizeB + marginB)*2, yB, image=boiler_on, anchor="nw")
img4 = canvas.create_image(xB + (sizeB + marginB)*3, yB, image=boiler_on, anchor="nw")
img5 = canvas.create_image(xB + (sizeB + marginB)*4, yB, image=boiler_on, anchor="nw")
img6 = canvas.create_image(xB + (sizeB + marginB)*5, yB, image=boiler_on, anchor="nw")

download_button = Button(root, text='Загрузить данные', bg='white', command=open_file)
download_button.place(relx=0.95, rely=0.95, anchor=SE) #использовал rely relx
root.mainloop()