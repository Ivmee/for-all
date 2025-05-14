import tkinter as tk
from tkinter import messagebox
import math

def start_simulation():
    try:
        speed = float(speed_entry.get())
        angle = float(angle_entry.get())
    except ValueError:
        messagebox.showerror("Ошибка", "Пожалуйста, введите числовые значения.")
        return

    if speed <= 0:
        messagebox.showerror("Ошибка", "Скорость должна быть положительной.")
        return

    if angle < 0 or angle > 90:
        messagebox.showerror("Ошибка", "Угол должен быть от 0 до 90 градусов.")
        return

    theta = math.radians(angle)
    g = 9.81
    vx = speed * math.cos(theta)
    vy = speed * math.sin(theta)

    t_total = (2 * vy) / g
    h_max = (vy ** 2) / (2 * g)
    range_x = vx * t_total

    result_label.config(text=f"Максимальная высота: {h_max:.2f} м\nДальность: {range_x:.2f} м")

    canvas.delete("all")

    canvas_width = 600
    canvas_height = 400
    padding = 20
    effective_width = canvas_width - 2 * padding
    effective_height = canvas_height - 2 * padding

    scale_x = effective_width / range_x if range_x != 0 else 1
    scale_y = effective_height / h_max if h_max > 0 else 1

    ball_radius = 5
    ball = canvas.create_oval(
        padding - ball_radius,
        canvas_height - padding - ball_radius,
        padding + ball_radius,
        canvas_height - padding + ball_radius,
        fill='red'
    )
    trajectory_line = canvas.create_line([], fill='blue', width=2)

    t = 0.0
    dt = 0.05
    x, y = 0.0, 0.0

    def animate():
        nonlocal t, x, y
        if y < 0:
            return

        t += dt
        x = vx * t
        y = vy * t - 0.5 * g * t ** 2

        if y < 0:
            t = (2 * vy) / g
            x = vx * t
            y = 0.0

        x_canvas = padding + x * scale_x
        y_canvas = canvas_height - padding - y * scale_y

        canvas.coords(
            ball,
            x_canvas - ball_radius,
            y_canvas - ball_radius,
            x_canvas + ball_radius,
            y_canvas + ball_radius
        )

        current_coords = canvas.coords(trajectory_line)
        current_coords.extend([x_canvas, y_canvas])
        canvas.coords(trajectory_line, current_coords)

        if y > 0:
            canvas.after(50, animate)

    animate()

root = tk.Tk()
root.title("Симулятор траектории снаряда")

input_frame = tk.Frame(root)
input_frame.pack(padx=10, pady=10)

speed_label = tk.Label(input_frame, text="Начальная скорость (м/с):")
speed_label.grid(row=0, column=0, sticky="e")
speed_entry = tk.Entry(input_frame)
speed_entry.grid(row=0, column=1, padx=5, pady=5)

angle_label = tk.Label(input_frame, text="Угол запуска (градусы):")
angle_label.grid(row=1, column=0, sticky="e")
angle_entry = tk.Entry(input_frame)
angle_entry.grid(row=1, column=1, padx=5, pady=5)

simulate_button = tk.Button(input_frame, text="Симулировать", command=start_simulation)
simulate_button.grid(row=2, column=0, columnspan=2, pady=10)

canvas = tk.Canvas(root, width=600, height=400, bg='white')
canvas.pack()

result_label = tk.Label(root, text="Максимальная высота: -\nДальность: -")
result_label.pack(pady=10)

root.mainloop()