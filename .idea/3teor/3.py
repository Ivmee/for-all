import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.integrate import odeint

# --- 1. ПАРАМЕТРЫ СИСТЕМЫ ---
N = 5              # Количество подвижных частиц
m0 = 1.0            # Базовая масса
k = 50.0            # Жесткость пружин
L = 1.0             # Равновесное расстояние между частицами (длина пружины)
t_max = 20          # Время симуляции
dt = 0.05           # Шаг времени для анимации

# Массив масс: m, 2m, 3m ... Nm
masses = np.array([(i + 1) * m0 for i in range(N)])

# --- 2. УРАВНЕНИЯ ДВИЖЕНИЯ ---
def system_equations(state, t):
    """
    state: массив размером 2N.
    Первые N элементов — смещения x_i от положения равновесия.
    Вторые N элементов — скорости v_i.
    """
    x = state[:N]
    v = state[N:]
    
    # Добавляем фиктивные нули слева и справа (стены)
    # Теперь массив x_padded имеет вид [0, x1, x2 ... xN, 0]
    x_padded = np.concatenate(([0], x, [0]))
    
    # Расчет ускорений по 2-му закону Ньютона
    # F_n = k * (x_{n-1} - 2*x_n + x_{n+1})
    # Сдвигаем массивы для векторизации:
    # x_{n-1} это x_padded[:-2]
    # x_{n+1} это x_padded[2:]
    # x_n     это x (или x_padded[1:-1])
    
    forces = k * (x_padded[:-2] - 2 * x + x_padded[2:])
    
    # a = F / m (где m — массив разных масс!)
    accel = forces / masses
    
    # Возвращаем производную состояния [v, a]
    return np.concatenate((v, accel))

# --- 3. НАЧАЛЬНЫЕ УСЛОВИЯ ---
x0 = np.zeros(N)
v0 = np.zeros(N)

# "Пнем" первый (самый легкий) шарик, чтобы запустить волну
x0[0] = 0.8  
# Или можно задать моду: 
# x0 = np.array([np.sin(i) for i in range(N)])

state0 = np.concatenate((x0, v0))
t = np.arange(0, t_max, dt)

# Интегрирование (решение уравнений)
solution = odeint(system_equations, state0, t)
displacement_data = solution[:, :N]

# --- 4. ВИЗУАЛИЗАЦИЯ ---
fig, ax = plt.subplots(figsize=(10, 4))
ax.set_xlim(-0.5, N * L + 1.5)
ax.set_ylim(-1, 1)
ax.set_title(f"Колебания цепочки с массами m, 2m, ... {N}m")
ax.set_xlabel("Положение")
ax.get_yaxis().set_visible(False)

# Рисуем стены
ax.plot([0, 0], [-0.5, 0.5], 'k-', linewidth=5)             # Левая стена
ax.plot([(N+1)*L, (N+1)*L], [-0.5, 0.5], 'k-', linewidth=5) # Правая стена

# Элементы графика, которые будем обновлять
springs_line, = ax.plot([], [], 'o-', color='gray', lw=1, markersize=0) # Линии пружин

# Создаем точки для шариков разного размера
particles = []
for i in range(N):
    # Размер точки пропорционален массе (визуальный эффект)
    size = 10 + 3 * masses[i] 
    p, = ax.plot([], [], 'o', color='crimson', markersize=size)
    particles.append(p)

def update(frame):
    current_displacements = displacement_data[frame]
    
    # Абсолютные координаты шариков:
    # Равновесное положение (i+1)*L + Смещение
    positions = [(i + 1) * L + current_displacements[i] for i in range(N)]
    
    # Координаты всех узлов (включая стены для рисовки пружин)
    all_x = [0] + positions + [(N+1)*L]
    all_y = [0] * (N + 2)
    
    # Обновляем пружины
    springs_line.set_data(all_x, all_y)
    
    # Обновляем шарики
    for i, p in enumerate(particles):
        p.set_data([positions[i]], [0])
        
    return [springs_line] + particles

ani = FuncAnimation(fig, update, frames=len(t), interval=30, blit=True)

plt.grid(True, axis='x', linestyle='--', alpha=0.3)
plt.show()