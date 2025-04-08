from tkinter import *

def fullscreen_on(event):
    root.attributes('-fullscreen', True)

def fullscreen_off(event):
    root.attributes('-fullscreen', False)

root = Tk()

root['bg'] = 'black'
root.title('Визуализация системы')

w = root.winfo_screenwidth()
h = root.winfo_screenheight()-80

root.geometry(f'{w}x{h}+0+0')

root.bind('<f>', fullscreen_on)
root.bind('<Escape>', fullscreen_off)

download_button = Button(root, text='Загрузить данные', bg='white')
download_button.place(x=w-120,y=h)

root.mainloop()