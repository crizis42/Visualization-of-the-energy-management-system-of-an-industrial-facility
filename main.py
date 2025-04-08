from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showinfo, showerror

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


root.bind('<F11>', fullscreen)

# Создаем холст (Canvas) для рисования
canvas = Canvas(root, bg='black', highlightthickness=0)
canvas.place(x=0, y=0, width=w, height=h)  # Растягиваем на весь экран

# Установки ГТУ
gap = w*0.05
square1 = canvas.create_rectangle(0, 0, 200, 200, fill='blue', outline='white')
square2 = canvas.create_rectangle(200, 0, 400, 200, fill='red', outline='white')
square3 = canvas.create_rectangle(400, 0, 600, 200, fill='red', outline='white')
square4 = canvas.create_rectangle(600, 0, 800, 200, fill='red', outline='white')
square5 = canvas.create_rectangle(800, 0, 1000, 200, fill='red', outline='white')
square6 = canvas.create_rectangle(1000, 0, 1200, 200, fill='red', outline='white')
square7 = canvas.create_rectangle(1200, 0, 1400, 200, fill='red', outline='white')
square8 = canvas.create_rectangle(1400, 0, 1600, 200, fill='red', outline='white')
square9 = canvas.create_rectangle(1600, 0, 1800, 200, fill='red', outline='white')



download_button = Button(root, text='Загрузить данные', bg='white', command=open_file)
download_button.place(relx=0.95, rely=0.95, anchor=SE) #использовал rely relx

root.mainloop()