import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# --- 1. ПАРАМЕТРЫ СИСТЕМЫ ---
N = 40                  # Количество частиц
m0 = 0.5                # Базовая масса
k = 80.0                # Жесткость пружин (чуть мягче для визуализации)
L = 1.0                 # Расстояние между частицами
dt = 0.03               # Шаг времени физики (маленький для точности)
steps_per_frame = 5     # Сколько шагов физики делать за 1 кадр видео (для скорости)

# Массы: растут арифметически (m, 2m, ..., 40m)
masses = np.array([(i + 1) * m0 for i in range(N)])

# --- 2. ПЕРЕМЕННЫЕ СОСТОЯНИЯ (Глобальные) ---
# Начальное положение: гауссов импульс слева
x = np.zeros(N)
v = np.zeros(N)
for i in range(N):
    x[i] = 2.5 * np.exp(-0.5 * ((i - 3)**2))

# --- 3. ФИЗИЧЕСКИЙ ДВИЖОК (Симплектический Эйлер) ---
def step_physics():
    global x, v
    
    # Чтобы система не разгонялась до бесконечности из-за численных ошибок,
    # добавим крошечное затухание (трение). В реальной физике оно всегда есть.
    damping = 0.0005 
    
    # 1. Расчет сил
    # Добавляем нули (стены) по краям
    x_pad = np.concatenate(([0], x, [0]))
    
    # F_i = k(x_{i-1} - x_i) + k(x_{i+1} - x_i)
    # Это сводится к k * (x_left + x_right - 2*x_center)
    forces = k * (x_pad[:-2] + x_pad[2:] - 2 * x)
    
    # 2. Второй закон Ньютона: a = F / m
    accel = forces / masses
    
    # 3. Интегрирование (Симплектический метод для сохранения энергии)
    v = v + accel * dt        # Обновляем скорость
    v = v * (1 - damping)     # Применяем легкое затухание
    x = x + v * dt            # Обновляем позицию, используя НОВУЮ скорость

# --- 4. НАСТРОЙКА ГРАФИКИ ---
plt.style.use('dark_background') # Так красивее и профессиональнее
fig, ax = plt.subplots(figsize=(12, 6))

# Настройки осей
ax.set_xlim(-1, N * L + 1)
ax.set_ylim(-4, 4)
ax.set_title(f"REAL-TIME SIMULATION: Inhomogeneous Lattice (N={N})\nClick to disturb!", color='white')
ax.set_xlabel("Particle Index (Mass increases $\\rightarrow$)", color='gray')
ax.set_yticks([])
ax.axis('off') # Убираем рамки, оставляем только суть

# Стены
ax.axvline(0, color='white', lw=3, alpha=0.5)
ax.axvline((N+1)*L, color='white', lw=3, alpha=0.5)

# Элементы визуализации
# Пружина
spring_line, = ax.plot([], [], '-', color='cyan', lw=1, alpha=0.4)

# Частицы
colors = np.linspace(0.3, 1, N) # Градиент цвета
sizes = np.linspace(30, 300, N) # Градиент размера

# Инициализация Scatter plot с правильными размерами
x_init_coords = np.array([(i + 1) * L + x[i] for i in range(N)])
y_init_coords = np.zeros(N)
scatter = ax.scatter(x_init_coords, y_init_coords, s=sizes, c=colors, cmap='plasma', edgecolors='white', zorder=10)

# --- 5. ОБРАБОТКА КЛИКА МЫШИ ---
def on_click(event):
    global v, x
    if event.xdata is None: return
    
    # Находим ближайшую частицу к месту клика
    click_pos = event.xdata
    # Примерный индекс частицы (так как L=1)
    idx = int(round(click_pos)) - 1
    
    if 0 <= idx < N:
        # Даем "пинок" скорости
        # Направление зависит от того, выше или ниже оси кликнули
        direction = 1 if event.ydata > 0 else -1
        v[idx] += 3.0 * direction # Резкое изменение скорости
        
        # Визуальный эффект в консоли
        print(f"Boom! Particle {idx} kicked.")

fig.canvas.mpl_connect('button_press_event', on_click)

# --- 6. ЦИКЛ АНИМАЦИИ ---
def update(frame):
    # Делаем несколько шагов физики на один кадр отрисовки,
    # чтобы симуляция была быстрой и плавной
    for _ in range(steps_per_frame):
        step_physics()
    
    # --- Отрисовка ---
    # Пересчитываем координаты для графика
    current_x_coords = np.array([(i + 1) * L + x[i] for i in range(N)])
    current_y_coords = np.zeros(N)
    
    # Обновляем точки
    offsets = np.column_stack((current_x_coords, current_y_coords))
    scatter.set_offsets(offsets)
    
    # Обновляем цвет шариков в зависимости от их скорости (визуализация энергии)
    # Нормализуем скорость для цвета
    v_norm = np.clip(np.abs(v) / 2.0, 0, 1)
    scatter.set_array(v_norm) 
    
    # Обновляем пружину
    all_x = np.concatenate(([0], current_x_coords, [(N+1)*L]))
    all_y = np.zeros(N + 2)
    spring_line.set_data(all_x, all_y)
    
    return spring_line, scatter

# interval=16 мс соответствует примерно 60 FPS
ani = FuncAnimation(fig, update, frames=None, blit=True, interval=16)

print("Симуляция запущена. Нажмите на график, чтобы возмутить систему.")
plt.show()
