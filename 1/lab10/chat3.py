import tkinter as tk
from tkinter import messagebox
import math
import time

# Константы
GRAVITY = 9.81  # ускорение свободного падения (м/с^2)

class ProjectileSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Симулятор траектории снаряда")

        # Масштаб и размеры холста по умолчанию
        self.scale = 5
        self.canvas_width = 1500
        self.canvas_height = 600

        # Флаг для паузы и остановки
        self.running = False
        self.simulation_active = False

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

        tk.Label(self.root, text="Коэффициент сопротивления воздуха (0-1):").grid(row=2, column=0)
        self.drag_entry = tk.Entry(self.root)
        self.drag_entry.insert(0, "0")
        self.drag_entry.grid(row=2, column=1)

        # Ползунок для масштаба
        tk.Label(self.root, text="Масштаб (пикселей/м):").grid(row=3, column=0)
        self.scale_slider = tk.Scale(self.root, from_=1, to=20, orient=tk.HORIZONTAL, command=self.update_scale)
        self.scale_slider.set(self.scale)
        self.scale_slider.grid(row=3, column=1)

        # Кнопки управления
        self.simulate_button = tk.Button(self.root, text="Симулировать", command=self.start_simulation)
        self.simulate_button.grid(row=4, column=0, pady=5)

        self.pause_button = tk.Button(self.root, text="Пауза", command=self.toggle_pause)
        self.pause_button.grid(row=4, column=1, pady=5)

        self.resume_button = tk.Button(self.root, text="Возобновить", command=self.resume_simulation)
        self.resume_button.grid(row=4, column=2, pady=5)

        self.reset_button = tk.Button(self.root, text="Сброс", command=self.reset_simulation)
        self.reset_button.grid(row=4, column=3, pady=5)

        # Холст
        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.grid(row=5, column=0, columnspan=4)

        # Метка для вывода результатов
        self.result_label = tk.Label(self.root, text="")
        self.result_label.grid(row=6, column=0, columnspan=4)

    def update_scale(self, val):
        self.scale = int(val)

    def toggle_pause(self):
        self.running = False

    def resume_simulation(self):
        if not self.simulation_active:
            return
        self.running = True
        self.root.after(100, self.simulate_step)

    def reset_simulation(self):
        self.running = False
        self.simulation_active = False
        self.canvas.delete("all")
        self.result_label.config(text="")

    def start_simulation(self):
        self.running = True
        self.simulation_active = True
        self.canvas.delete("all")
        self.result_label.config(text="")

        try:
            self.v0 = float(self.speed_entry.get())
            self.angle_deg = float(self.angle_entry.get())
            self.drag = float(self.drag_entry.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные числовые значения.")
            return

        if not (0 <= self.drag <= 1):
            messagebox.showerror("Ошибка", "Сопротивление воздуха должно быть в диапазоне от 0 до 1.")
            return

        if self.v0 <= 0 or self.scale <= 0:
            messagebox.showerror("Ошибка", "Скорость и масштаб должны быть положительными")
            return

        angle_rad = math.radians(self.angle_deg)
        self.vx = self.v0 * math.cos(angle_rad)
        self.vy = self.v0 * math.sin(angle_rad)

        self.t = 0
        self.dt = 0.05
        self.x, self.y = 0, 0
        self.points = []

        self.simulate_step()

    def simulate_step(self):
        if not self.running or self.y < 0:
            return

        speed = math.sqrt(self.vx**2 + self.vy**2)
        self.vx -= self.drag * self.vx * self.dt
        self.vy -= self.drag * self.vy * self.dt

        self.x += self.vx * self.dt
        self.vy -= GRAVITY * self.dt
        self.y += self.vy * self.dt

        if self.y < 0:
            max_height = max((self.canvas_height - p[1]) / self.scale for p in self.points)
            range_ = self.x
            self.result_label.config(
                text=f"Максимальная высота: {max_height:.2f} м, Дальность: {range_:.2f} м"
            )
            return

        canvas_x = self.x * self.scale
        canvas_y = self.canvas_height - self.y * self.scale
        self.points.append((canvas_x, canvas_y))

        if len(self.points) > 1:
            self.canvas.create_line(
                self.points[-2][0], self.points[-2][1],
                self.points[-1][0], self.points[-1][1],
                fill="blue"
            )

        self.canvas.update()
        self.root.after(10, self.simulate_step)

if __name__ == "__main__":
    root = tk.Tk()
    app = ProjectileSimulator(root)
    root.mainloop()
