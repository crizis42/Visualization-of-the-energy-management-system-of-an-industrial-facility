from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showinfo, showerror


root = Tk()

root['bg'] = 'black'
root.title('Визуализация системы')

w = root.winfo_screenwidth()
h = root.winfo_screenheight()-80

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

download_button = Button(text='Загрузить данные', bg='white', command=open_file)
download_button.place(x=w-120,y=h)





root.mainloop()