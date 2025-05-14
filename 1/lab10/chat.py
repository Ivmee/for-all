import tkinter as tk
from tkinter import messagebox
import math
import time

# Константы
GRAVITY = 9.81  # ускорение свободного падения (м/с^2)
SCALE = 5       # масштаб (пиксели на метр)

class ProjectileSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Симулятор траектории снаряда")

        # Интерфейс
        self.create_widgets()

    def create_widgets(self):
        # Поля ввода
        tk.Label(self.root, text="Начальная скорость (м/с):").grid(row=0, column=0)
        self.speed_entry = tk.Entry(self.root)
        self.speed_entry.grid(row=0, column=1)

        tk.Label(self.root, text="Угол запуска (градусы):").grid(row=1, column=0)
        self.angle_entry = tk.Entry(self.root)
        self.angle_entry.grid(row=1, column=1)

        # Кнопка симуляции
        self.simulate_button = tk.Button(self.root, text="Симулировать", command=self.simulate)
        self.simulate_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Холст
        self.canvas = tk.Canvas(self.root, width=800, height=400, bg="white")
        self.canvas.grid(row=3, column=0, columnspan=2)

        # Метка для вывода результатов
        self.result_label = tk.Label(self.root, text="")
        self.result_label.grid(row=4, column=0, columnspan=2)

    def simulate(self):
        # Очистка холста и метки
        self.canvas.delete("all")
        self.result_label.config(text="")

        try:
            v0 = float(self.speed_entry.get())
            angle_deg = float(self.angle_entry.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Введите числовые значения для скорости и угла")
            return

        if v0 <= 0:
            messagebox.showerror("Ошибка", "Начальная скорость должна быть положительной")
            return

        angle_rad = math.radians(angle_deg)
        vx = v0 * math.cos(angle_rad)
        vy = v0 * math.sin(angle_rad)

        t = 0
        dt = 0.05  # шаг времени (сек)
        x, y = 0, 0
        points = []

        while y >= 0:
            x = vx * t
            y = vy * t - 0.5 * GRAVITY * t**2
            if y < 0:
                break
            canvas_x = x * SCALE
            canvas_y = 400 - y * SCALE  # инвертируем y для экрана
            points.append((canvas_x, canvas_y))
            t += dt

        # Анимация траектории
        for i in range(1, len(points)):
            self.canvas.create_line(points[i-1][0], points[i-1][1],
                                    points[i][0], points[i][1], fill="blue")
            self.canvas.update()
            time.sleep(0.01)

        # Расчёт и вывод результатов
        max_height = (vy ** 2) / (2 * GRAVITY)
        range_ = (v0 ** 2) * math.sin(2 * angle_rad) / GRAVITY
        self.result_label.config(
            text=f"Максимальная высота: {max_height:.2f} м, Дальность: {range_:.2f} м"
        )

if __name__ == "__main__":
    root = tk.Tk()
    app = ProjectileSimulator(root)
    root.mainloop()