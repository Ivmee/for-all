from tkinter import *

def clicked():
    """Функция обработки нажатия кнопки"""
    res = f"Вы написали: {txt.get()}, значение ползунка: {w_vertical.get()}, {w_horizontal.get()}"
    lbl.configure(text=res)

# Создаем главное окно
root = Tk()
root.title("Добро пожаловать в Tkinter")
root.geometry('450x250')  # Увеличил размер окна

# Создаем меню
menu = Menu(root)
file_menu = Menu(menu, tearoff=0)
file_menu.add_command(label='Новый')
file_menu.add_separator()
file_menu.add_command(label='Выход', command=root.quit)
menu.add_cascade(label='Файл', menu=file_menu)
root.config(menu=menu)

# Создаем и размещаем элементы интерфейса
lbl = Label(root, text="Введите текст:")
lbl.grid(column=0, row=0, padx=5, pady=5)

txt = Entry(root, width=20)
txt.grid(column=1, row=0, padx=5, pady=5)

btn = Button(root, text="Подтвердить", command=clicked)
btn.grid(column=2, row=0, padx=5, pady=5)

# Вертикальный ползунок
w_vertical = Scale(root, from_=0, to=42, label="Вертикальный", orient=VERTICAL)
w_vertical.grid(column=0, row=1, padx=10, pady=10)

# Горизонтальный ползунок
w_horizontal = Scale(root, from_=0, to=200, label="Горизонтальный", orient=HORIZONTAL, length=200)
w_horizontal.grid(column=1, row=1, columnspan=2, padx=10, pady=10)

# Запускаем главный цикл
root.mainloop()