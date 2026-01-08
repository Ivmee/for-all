import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, RadioButtons, Slider
from scipy.signal import find_peaks
from scipy.optimize import curve_fit
import os

# =========================================================================
# 1. ФИЗИКА И КАЛИБРОВКА
# =========================================================================
d = 4.0e-3        # Толщина (м)
n_ref = 1.4567    # Показатель преломления
h = 6.62607e-34   # Постоянная Планка
c = 2.99792e8     # Скорость света
mu_B_theor = 9.274e-24 

# Калибровка (А -> мТл)
CALIB_I =  [0.0, 0.5, 0.8, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0] 
CALIB_B_mT = [0.0, 40,  80,  100, 150, 200, 250, 301, 340, 392, 473]

script_dir = os.path.dirname(os.path.abspath(__file__))

def current_to_B(I):
    return np.interp(I, CALIB_I, CALIB_B_mT) / 1000.0

# =========================================================================
# 2. ОБРАБОТКА ИЗОБРАЖЕНИЙ (АВТО-ЯРКОСТЬ)
# =========================================================================

def auto_contrast(img_gray):
    """
    Автоматическое выравнивание гистограммы (CLAHE).
    Делает кольца видными и на темных, и на светлых фото.
    """
    # ClipLimit=2.0 - сила контраста, TileGridSize - размер окна
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    return clahe.apply(img_gray)

def find_center_smart(img_gray):
    """Поиск центра с предварительной авто-коррекцией"""
    try:
        enhanced = auto_contrast(img_gray)
        blurred = cv2.GaussianBlur(enhanced, (11, 11), 0)
        # Адаптивный порог
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 51, 2)
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        cx_list, cy_list = [], []
        h, w = img_gray.shape
        
        for cnt in contours:
            if len(cnt) < 50: continue 
            (x, y), r = cv2.minEnclosingCircle(cnt)
            # Ищем кольца среднего размера по центру
            if 40 < r < w/1.8: 
                if abs(x - w/2) < w/4 and abs(y - h/2) < h/4:
                    cx_list.append(x); cy_list.append(y)
        
        if cx_list: 
            return int(np.median(cx_list)), int(np.median(cy_list))
    except:
        pass
    return img_gray.shape[1]//2, img_gray.shape[0]//2

def get_profile(img, center):
    cX, cY = center
    Y, X = np.ogrid[:img.shape[0], :img.shape[1]]
    r_map = np.sqrt((X - cX)**2 + (Y - cY)**2)
    r_int = r_map.astype(int)
    max_r = int(np.max(r_int))
    
    tbin = np.bincount(r_int.ravel(), img.ravel(), minlength=max_r+1)
    nr = np.bincount(r_int.ravel(), minlength=max_r+1)
    
    profile = np.zeros_like(tbin, dtype=float)
    mask = nr > 0
    profile[mask] = tbin[mask] / nr[mask]
    return profile

def refine_peak(profile, idx):
    """Субпиксельное уточнение верхушки пика"""
    if idx <= 0 or idx >= len(profile) - 1: return idx
    y1, y2, y3 = float(profile[idx-1]), float(profile[idx]), float(profile[idx+1])
    denom = y1 - 2*y2 + y3
    if denom == 0: return idx
    return idx + (y1 - y3) / (2*denom)

# =========================================================================
# 3. GUI ПРИЛОЖЕНИЕ
# =========================================================================
class LabApp:
    def __init__(self, files):
        self.files = files
        self.data = []
        self.idx = 0
        self.mode = 'triplet' 
        self.prominence = 3.0 # Начальный порог поиска пиков
        
        print("--- ЗАГРУЗКА ---")
        for name, I in files:
            path = os.path.join(script_dir, name)
            if not os.path.exists(path):
                print(f"❌ Пропущен: {name}")
                continue
            
            raw_img = cv2.imread(path)
            if raw_img is None: continue
            gray = raw_img[:,:,2]
            
            # Сразу применяем авто-контраст
            processed_img = auto_contrast(gray)
            center = find_center_smart(gray)
            
            self.data.append({
                'name': name, 'I': I, 'B': current_to_B(I),
                'img_raw': gray,
                'img_proc': processed_img,
                'center': center,
                'res': None
            })
            print(f"OK: {name}")
            
        if not self.data: return

        # === ИНТЕРФЕЙС ===
        self.fig = plt.figure(figsize=(18, 10), facecolor='#f0f0f0')
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        
        gs = self.fig.add_gridspec(3, 2, height_ratios=[1, 1, 0.25], hspace=0.35, wspace=0.15)
        
        self.ax_img = self.fig.add_subplot(gs[0, 0])
        self.ax_prof = self.fig.add_subplot(gs[0, 1])
        self.ax_table = self.fig.add_subplot(gs[1, 0])
        self.ax_final = self.fig.add_subplot(gs[1, 1])
        
        # Панель управления
        gs_ctrl = gs[2, :].subgridspec(1, 4, width_ratios=[0.5, 1.5, 0.5, 0.5], wspace=0.2)
        
        # Радио
        ax_radio = self.fig.add_subplot(gs_ctrl[0])
        ax_radio.set_facecolor('#f0f0f0')
        self.radio = RadioButtons(ax_radio, ('Триплет', 'Дублет'))
        self.radio.on_clicked(self.change_mode)
        for s in ax_radio.spines.values(): s.set_visible(False)
        
        # Слайдер ПОРОГА (Самый важный!)
        ax_sl_cont = self.fig.add_subplot(gs_ctrl[1])
        ax_sl_cont.axis('off')
        ax_sl = ax_sl_cont.inset_axes([0.0, 0.5, 1.0, 0.2])
        self.slider = Slider(ax_sl, 'Чувствительность (Порог пиков) ', 0.5, 20.0, valinit=3.0)
        self.slider.on_changed(self.update_prominence)
        
        # Кнопки
        self.btn_prev = Button(self.fig.add_subplot(gs_ctrl[2]), '< Назад')
        self.btn_next = Button(self.fig.add_subplot(gs_ctrl[3]), 'Вперед >')
        self.btn_prev.on_clicked(self.prev_img)
        self.btn_next.on_clicked(self.next_img)

        self.recalc_all()
        self.update_view()
        plt.show()

    def recalc_all(self):
        for i in range(len(self.data)):
            self.process_frame(i)
            
    def process_frame(self, i):
        d = self.data[i]
        prof = get_profile(d['img_proc'], d['center'])
        
        # Поиск пиков с регулируемым порогом (prominence)
        peaks_int, _ = find_peaks(prof, prominence=self.prominence, distance=6)
        peaks_sub = np.array([refine_peak(prof, p) for p in peaks_int])
        
        r_sq = peaks_sub**2
        step = 3 if self.mode == 'triplet' else 2
        n_groups = len(peaks_sub) // step
        
        calc_data = []
        deltas, Deltas = [], []
        
        for k in range(n_groups):
            idxs = range(k*step, k*step + step)
            g_r2 = r_sq[idxs]
            
            delta = 0
            Delta = None
            
            # --- ЛОГИКА ТРИПЛЕТА ---
            if self.mode == 'triplet':
                # delta = среднее расстояние от центрального до боковых (в квадратах)
                delta = ((g_r2[1]-g_r2[0]) + (g_r2[2]-g_r2[1])) / 2.0
                
                # Delta = расстояние до центрального пика следующего порядка
                if k < n_groups - 1:
                    r2_pi_next = r_sq[(k+1)*3 + 1]
                    Delta = r2_pi_next - g_r2[1]
            
            # --- ЛОГИКА ДУБЛЕТА ---
            else:
                delta = (g_r2[1] - g_r2[0]) / 2.0
                if k < n_groups - 1:
                    mean_curr = np.mean(g_r2)
                    mean_next = np.mean(r_sq[(k+1)*2 : (k+1)*2 + 2])
                    Delta = mean_next - mean_curr

            # --- ФИЛЬТР ОШИБОК ---
            # delta не может быть больше Delta (это физически невозможно для Зеемана)
            # Также delta не может быть отрицательной
            valid = False
            if Delta is not None and delta > 0 and delta < Delta * 0.8:
                valid = True
                deltas.append(delta)
                Deltas.append(Delta)
                
            calc_data.append({
                'k': k+1, 'delta': delta, 'Delta': Delta, 'valid': valid,
                'r_peaks': peaks_sub[idxs] # Сохраняем радиусы для отрисовки
            })
        
        # Итоговая статистика кадра
        ratio, ratio_err = None, None
        if deltas and Deltas:
            mean_d, mean_D = np.mean(deltas), np.mean(Deltas)
            # Стандартная ошибка
            sem_d = np.std(deltas, ddof=1)/np.sqrt(len(deltas)) if len(deltas)>1 else mean_d*0.05
            sem_D = np.std(Deltas, ddof=1)/np.sqrt(len(Deltas)) if len(Deltas)>1 else mean_D*0.05
            
            ratio = mean_d / mean_D
            ratio_err = ratio * np.sqrt((sem_d/mean_d)**2 + (sem_D/mean_D)**2)
        
        d['res'] = {
            'peaks': peaks_sub, 'prof': prof, 
            'calc_data': calc_data, 
            'ratio': ratio, 'ratio_err': ratio_err
        }

    def update_prominence(self, val):
        self.prominence = val
        self.recalc_all()
        self.update_view()

    def update_view(self):
        d = self.data[self.idx]
        res = d['res']
        
        # 1. КАРТИНКА (УЖЕ АВТО-КОНТРАСТНАЯ)
        self.ax_img.clear()
        self.ax_img.imshow(d['img_proc'], cmap='gray')
        self.ax_img.scatter(*d['center'], c='lime', marker='+', s=120, lw=2)
        self.ax_img.set_title(f"Фото: {d['name']} (I={d['I']} A)", fontsize=11, fontweight='bold')
        self.ax_img.axis('off')
        
        # Рисуем только валидные кольца
        if res['calc_data']:
            for row in res['calc_data']:
                color = 'lime' if row['valid'] else 'red' # Зеленые - ок, Красные - отброшены
                for r in row['r_peaks']:
                    self.ax_img.add_patch(plt.Circle(d['center'], r, color=color, fill=False, lw=1))

        # 2. ПРОФИЛЬ С ВИЗУАЛИЗАЦИЕЙ delta/Delta
        self.ax_prof.clear()
        self.ax_prof.plot(res['prof'], color='#333', lw=1, alpha=0.6)
        
        # Рисуем отметки расчетов
        if res['calc_data']:
            for row in res['calc_data']:
                if row['valid']:
                    rs = row['r_peaks']
                    # Рисуем синюю линию (delta) внутри триплета
                    y_h = np.max(res['prof'][rs.astype(int)])
                    self.ax_prof.plot(rs, [y_h]*len(rs), 'b-', lw=2, alpha=0.7)
                    self.ax_prof.text(rs[1], y_h+5, "δ", color='blue', ha='center', fontsize=8)
        
        self.ax_prof.set_title(f"Профиль (Найдено групп: {len(res['calc_data'])})", fontsize=10)
        self.ax_prof.grid(True, alpha=0.3)

        # 3. ТАБЛИЦА
        self.ax_table.clear()
        self.ax_table.axis('off')
        
        lines = [f"Результаты (Режим: {self.mode})"]
        lines.append(f"{'№':<3}| {'delta':<7}| {'Delta':<7}| {'Статус'}")
        lines.append("-" * 35)
        
        valid_cnt = 0
        if res['calc_data']:
            for row in res['calc_data']:
                d_val = f"{row['delta']:.0f}"
                D_val = f"{row['Delta']:.0f}" if row['Delta'] else "-"
                status = "OK" if row['valid'] else "BAD"
                if row['valid']: valid_cnt += 1
                lines.append(f"{row['k']:<3}| {d_val:<7}| {D_val:<7}| {status}")
            
            lines.append("-" * 35)
            if res['ratio']:
                lines.append(f"Отношение: {res['ratio']:.4f}")
                lines.append(f"Погрешн.:  {res['ratio_err']/res['ratio']*100:.1f}%")
            else:
                lines.append("Нет надежных данных")
        else:
            lines.append("ПИКИ НЕ НАЙДЕНЫ!")
            lines.append("--> Подвигайте слайдер 'Чувствительность'")
            lines.append("--> Или кликните в центр фото")

        self.ax_table.text(0.05, 0.95, "\n".join(lines), family='monospace', va='top', fontsize=10)

        # 4. ФИНАЛЬНЫЙ ГРАФИК
        self.draw_final_graph()
        self.fig.canvas.draw_idle()

    def draw_final_graph(self):
        self.ax_final.clear()
        Bs, Rs, Errs = [], [], []
        
        for item in self.data:
            if item['res'] and item['res']['ratio']:
                if item['B'] > 0.005: 
                    Bs.append(item['B'])
                    Rs.append(item['res']['ratio'])
                    Errs.append(item['res']['ratio_err'])
        
        self.ax_final.set_xlabel("Поле B (Тл)")
        self.ax_final.set_ylabel("delta / Delta")
        self.ax_final.grid(True, alpha=0.3)
        self.ax_final.set_title("Результат", fontsize=10)
        
        if len(Bs) > 1:
            Bs, Rs, Errs = np.array(Bs), np.array(Rs), np.array(Errs)
            
            # Аппроксимация через ноль
            def func(x, m): return m * x
            
            try:
                popt, pcov = curve_fit(func, Bs, Rs, sigma=Errs, absolute_sigma=True)
            except:
                popt, pcov = curve_fit(func, Bs, Rs)
            
            m = popt[0]
            m_err = np.sqrt(np.diag(pcov))[0]
            
            const_part = (h * c) / (2 * d * n_ref)
            mu_calc = m * const_part
            mu_err = m_err * const_part
            
            err_pct = (mu_err / mu_calc) * 100
            diff_pct = abs(mu_calc - mu_B_theor) / mu_B_theor * 100
            
            self.ax_final.errorbar(Bs, Rs, yerr=Errs, fmt='o', c='k', capsize=3, label='Данные')
            self.ax_final.plot(Bs, func(Bs, m), 'r--', label='Тренд')
            
            res_txt = (f"$\\mu_B = {mu_calc/1e-24:.2f} \pm {mu_err/1e-24:.2f}$\n"
                       f"($10^{{-24}}$ Дж/Тл)\n"
                       f"Ошибка: {err_pct:.1f}%\n"
                       f"Отклонение: {diff_pct:.1f}%")
            
            self.ax_final.text(0.05, 0.6, res_txt, transform=self.ax_final.transAxes, 
                               bbox=dict(facecolor='white', alpha=0.8), fontsize=9)
            self.ax_final.legend()
            
            # Текущая точка
            curr = self.data[self.idx]
            if curr['res']['ratio']:
                self.ax_final.scatter([curr['B']], [curr['res']['ratio']], s=100, edgecolors='b', facecolors='none', lw=2)

    def on_click(self, event):
        if event.inaxes == self.ax_img:
            self.data[self.idx]['center'] = (int(event.xdata), int(event.ydata))
            self.process_frame(self.idx)
            self.update_view()

    def change_mode(self, label):
        self.mode = 'triplet' if 'Триплет' in label else 'doublet'
        self.recalc_all()
        self.update_view()

    def next_img(self, event):
        self.idx = (self.idx + 1) % len(self.data)
        self.update_view()

    def prev_img(self, event):
        self.idx = (self.idx - 1) % len(self.data)
        self.update_view()

if __name__ == "__main__":
    # СПИСОК ФАЙЛОВ
    files = [
        ("0,5.jpg", 0.5),
        ("0,8.jpg", 0.8),
        ("1,1.jpg", 1.1),
        ("1,3.jpg", 1.3),
        ("1,5.jpg", 1.5),
        ("1,7.jpg", 1.7),
        ("1,9.jpg", 1.9),
        ("2,1.jpg", 2.1),
        ("2,3.jpg", 2.3),
        ("2,5.jpg", 2.5)
    ]
    
    app = LabApp(files)