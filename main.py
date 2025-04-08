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
margin = 10 #Отступы
size = 150 #Размер
x = 10
y = 10
canvas.create_rectangle(x, y, x + size, y + size, fill='blue', outline='white')
canvas.create_rectangle(x + size + margin, y, x + (size * 2) + margin, y + size, fill='blue', outline='white')
canvas.create_rectangle(x + (size * 2) + margin * 2, y, x + (size * 3) + margin, y + size, fill='blue', outline='white')
canvas.create_rectangle(x + (size * 3) + margin * 2, y, x + (size * 4) + margin, y + size, fill='blue', outline='white')
canvas.create_rectangle(x + (size * 4) + margin * 2, y, x + (size * 5) + margin, y + size, fill='blue', outline='white')
canvas.create_rectangle(x + (size * 5) + margin * 2, y, x + (size * 6) + margin, y + size, fill='blue', outline='white')
canvas.create_rectangle(x + (size * 6) + margin * 2, y, x + (size * 7) + margin, y + size, fill='blue', outline='white')
canvas.create_rectangle(x + (size * 7) + margin * 2, y, x + (size * 8) + margin, y + size, fill='blue', outline='white')
canvas.create_rectangle(x + (size * 8) + margin * 2, y, x + (size * 9) + margin, y + size, fill='blue', outline='white')





download_button = Button(root, text='Загрузить данные', bg='white', command=open_file)
download_button.place(relx=0.95, rely=0.95, anchor=SE) #использовал rely relx
root.mainloop()