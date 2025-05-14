import tkinter as tk
from tkinter import messagebox
import math

class ProjectileSimulator:
    def __init__(self, master):
        self.master = master
        master.title("Моделирование траектории снаряда")
        
        # Параметры симуляции
        self.g = 9.81  # ускорение свободного падения (м/с²)
        self.dt = 0.05  # шаг времени (с)
        self.scale = 5  # масштаб пикселей на метр
        self.width = 800
        self.height = 500
        self.ground_level = 450
        self.is_simulating = False
        self.is_paused = False
        self.air_resistance = False
        
        # Создание интерфейса
        self.create_widgets()
        
    def create_widgets(self):
        # Фрейм для элементов управления
        control_frame = tk.Frame(self.master)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        # Поля ввода
        tk.Label(control_frame, text="Начальная скорость (м/с):").grid(row=0, column=0, sticky=tk.W)
        self.velocity_entry = tk.Entry(control_frame)
        self.velocity_entry.grid(row=0, column=1, padx=5, pady=5)
        self.velocity_entry.insert(0, "20")
        
        tk.Label(control_frame, text="Угол запуска (градусы):").grid(row=1, column=0, sticky=tk.W)
        self.angle_entry = tk.Entry(control_frame)
        self.angle_entry.grid(row=1, column=1, padx=5, pady=5)
        self.angle_entry.insert(0, "45")
        
        # Чекбокс сопротивления воздуха
        self.air_resist_var = tk.BooleanVar()
        air_resist_check = tk.Checkbutton(
            control_frame, 
            text="Учитывать сопротивление воздуха", 
            variable=self.air_resist_var,
            command=self.toggle_air_resistance
        )
        air_resist_check.grid(row=2, column=0, columnspan=2, sticky=tk.W)
        
        # Кнопки управления
        self.simulate_button = tk.Button(control_frame, text="Симулировать", command=self.start_simulation)
        self.simulate_button.grid(row=3, column=0, pady=10)
        
        self.pause_button = tk.Button(
            control_frame, 
            text="Пауза", 
            command=self.toggle_pause,
            state=tk.DISABLED
        )
        self.pause_button.grid(row=3, column=1, pady=10)
        
        self.reset_button = tk.Button(
            control_frame, 
            text="Сброс", 
            command=self.reset_simulation,
            state=tk.DISABLED
        )
        self.reset_button.grid(row=3, column=2, pady=10)
        
        # Холст для отображения траектории
        self.canvas = tk.Canvas(
            self.master, 
            width=self.width, 
            height=self.height, 
            bg="white"
        )
        self.canvas.pack(padx=10, pady=10)
        
        # Рисуем землю
        self.canvas.create_line(
            0, self.ground_level, 
            self.width, self.ground_level, 
            fill="green", 
            width=10
        )
        
        # Метки для результатов
        self.result_label = tk.Label(self.master, text="", font=('Arial', 10))
        self.result_label.pack(side=tk.BOTTOM, pady=5)
        
    def toggle_air_resistance(self):
        self.air_resistance = self.air_resist_var.get()
        
    def toggle_pause(self):
        self.is_paused = not self.is_paused
        self.pause_button.config(text="Возобновить" if self.is_paused else "Пауза")
        if not self.is_paused:
            self.animate()
        
    def start_simulation(self):
        if self.is_simulating:
            return
            
        try:
            # Получаем входные данные
            v0 = float(self.velocity_entry.get())
            angle = float(self.angle_entry.get())
            
            if v0 <= 0:
                raise ValueError("Скорость должна быть положительной")
            if angle <= 0 or angle >= 90:
                raise ValueError("Угол должен быть между 0 и 90 градусами")
                
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", f"Некорректные данные: {e}")
            return
            
        # Инициализация параметров симуляции
        self.is_simulating = True
        self.is_paused = False
        self.simulate_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.NORMAL)
        
        # Преобразуем угол в радианы
        angle_rad = math.radians(angle)
        
        # Начальные условия
        self.x = 50  # начальная позиция по x (пиксели)
        self.y = self.ground_level - 50  # начальная позиция по y (пиксели)
        self.vx = v0 * math.cos(angle_rad)  # начальная скорость по x (м/с)
        self.vy = -v0 * math.sin(angle_rad)  # начальная скорость по y (м/с)
        self.time = 0
        
        # Очищаем холст и рисуем снаряд
        self.canvas.delete("all")
        self.canvas.create_line(
            0, self.ground_level, 
            self.width, self.ground_level, 
            fill="green", 
            width=2
        )
        
        self.projectile = self.canvas.create_oval(
            self.x , self.y ,
            self.x , self.y ,
            fill="red"
        )
        
        self.trajectory = []
        self.max_height = 0
        self.max_distance = 0
        
        # Запускаем анимацию
        self.animate()
        
    def animate(self):
        if not self.is_simulating or self.is_paused:
            return
            
        # Физические расчеты
        self.time += self.dt
        
        # Рассчитываем силы
        if self.air_resistance:
            # Упрощенная модель сопротивления воздуха
            speed = math.sqrt(self.vx**2 + self.vy**2)
            drag_force = 0.01 * speed**2  # коэффициент подобран экспериментально
            
            # Компоненты силы сопротивления
            drag_x = drag_force * self.vx / speed
            drag_y = drag_force * self.vy / speed
            
            # Ускорение с учетом сопротивления воздуха
            ax = -drag_x
            ay = self.g - drag_y
        else:
            # Без сопротивления воздуха
            ax = 0
            ay = self.g
            
        # Обновляем скорость
        self.vx += ax * self.dt
        self.vy += ay * self.dt
        
        # Обновляем позицию (в метрах)
        dx = self.vx * self.dt
        dy = self.vy * self.dt
        
        # Обновляем позицию (в пикселях)
        self.x += dx * self.scale
        self.y += dy * self.scale
        
        # Сохраняем точку траектории
        self.trajectory.append((self.x, self.y))
        
        # Обновляем максимальную высоту и дальность
        current_height = (self.ground_level - self.y) / self.scale
        current_distance = (self.x - 50) / self.scale
        
        if current_height > self.max_height:
            self.max_height = current_height
            
        if current_distance > self.max_distance:
            self.max_distance = current_distance
        
        # Проверяем, не упал ли снаряд
        if self.y >= self.ground_level - 10:
            self.y = self.ground_level - 10
            self.is_simulating = False
            self.show_results()
            
            # Рисуем точку удара
            self.canvas.create_oval(
                self.x - 8, self.y - 8,
                self.x + 8, self.y + 8,
                fill="black"
            )
            return
            
        # Обновляем позицию снаряда на холсте
        self.canvas.coords(self.projectile, 
                          self.x - 5, self.y - 5,
                          self.x + 5, self.y + 5)
        
        # Рисуем траекторию
        if len(self.trajectory) > 1:
            self.canvas.create_line(
                self.trajectory[-2][0], self.trajectory[-2][1],
                self.trajectory[-1][0], self.trajectory[-1][1],
                fill="blue",
                width=1
            )
        
        # Рисуем вектор скорости
        self.canvas.delete("velocity")
        arrow_length = 30
        v0 = float(self.velocity_entry.get())
        arrow_end_x = self.x + self.vx * arrow_length / (v0 * 2)
        arrow_end_y = self.y + self.vy * arrow_length / (v0 * 2)
        
        self.canvas.create_line(
            self.x, self.y,
            arrow_end_x, arrow_end_y,
            arrow=tk.LAST,
            fill="red",
            width=2,
            tags="velocity"
        )
        
        # Продолжаем анимацию
        self.master.after(20, self.animate)
        
    def show_results(self):
        result_text = (
            f"Максимальная высота: {self.max_height:.2f} м | "
            f"Дальность полета: {self.max_distance:.2f} м | "
            f"Время полета: {self.time:.2f} с"
        )
        self.result_label.config(text=result_text)
        
        # Активируем кнопки
        self.simulate_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        
    def reset_simulation(self):
        self.is_simulating = False
        self.is_paused = False
        self.canvas.delete("all")
        
        # Рисуем землю
        self.canvas.create_line(
            0, self.ground_level, 
            self.width, self.ground_level, 
            fill="green", 
            width=2
        )
        
        self.result_label.config(text="")
        self.simulate_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED, text="Пауза")
        self.reset_button.config(state=tk.DISABLED)

# Создаем и запускаем приложение
root = tk.Tk()
app = ProjectileSimulator(root)
root.mainloop()