import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, RadioButtons, Slider
from scipy.signal import find_peaks, savgol_filter
from scipy.optimize import curve_fit
import os
from datetime import datetime

# =========================================================================
# 1. ФИЗИЧЕСКИЕ КОНСТАНТЫ
# =========================================================================
d = 4.0e-3        # Толщина эталона (м)
n_ref = 1.4567    # Показатель преломления
h = 6.62607e-34   # Постоянная Планка
c = 2.99792e8     # Скорость света
mu_B_theor = 9.274e-24 

# Калибровка (А -> мТл)
CALIB_I =  [0.0, 0.5, 0.8, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0] 
CALIB_B_mT = [0.0, 40,  80,  100, 150, 200, 250, 301, 340, 392, 473]

script_dir = os.path.dirname(os.path.abspath(__file__))

def current_to_B(I):
    """Интерполяция тока в магнитное поле (Тл)"""
    return np.interp(I, CALIB_I, CALIB_B_mT) / 1000.0

# =========================================================================
# 2. АЛГОРИТМЫ ОБРАБОТКИ
# =========================================================================

def auto_contrast(img_gray):
    """CLAHE: Адаптивное выравнивание гистограммы"""
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    return clahe.apply(img_gray)

def find_center_smart(img_gray):
    """Поиск центра колец"""
    try:
        enhanced = auto_contrast(img_gray)
        blurred = cv2.GaussianBlur(enhanced, (11, 11), 0)
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 51, 2)
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        cx_list, cy_list = [], []
        h, w = img_gray.shape
        
        for cnt in contours:
            if len(cnt) < 50: continue 
            (x, y), r = cv2.minEnclosingCircle(cnt)
            if 40 < r < w/1.8: 
                if abs(x - w/2) < w/4 and abs(y - h/2) < h/4:
                    cx_list.append(x); cy_list.append(y)
        
        if cx_list: 
            return int(np.median(cx_list)), int(np.median(cy_list))
    except:
        pass
    return img_gray.shape[1]//2, img_gray.shape[0]//2

def get_profile(img, center):
    """Получение радиального профиля"""
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
    """Субпиксельное уточнение (парабола)"""
    if idx <= 0 or idx >= len(profile) - 1: return idx
    y1, y2, y3 = float(profile[idx-1]), float(profile[idx]), float(profile[idx+1])
    denom = y1 - 2*y2 + y3
    if denom == 0: return idx
    return idx + (y1 - y3) / (2*denom)

def cluster_peaks(peaks, max_distance=60):
    """Группирует пики по близости"""
    if len(peaks) == 0:
        return []
    groups = []
    current_group = [peaks[0]]
    for i in range(1, len(peaks)):
        # Если разница меньше max_distance, добавляем в текущую группу
        if peaks[i] - peaks[i-1] < max_distance:
            current_group.append(peaks[i])
        else:
            groups.append(current_group)
            current_group = [peaks[i]]
    groups.append(current_group)
    return groups

# =========================================================================
# 3. GUI ПРИЛОЖЕНИЕ
# =========================================================================
class LabApp:
    def __init__(self, file_list):
        self.data = []
        self.idx = 0
        self.mode = 'triplet' 
        self.prominence = 3.0 
        self.smooth_window = 5 
        self.cluster_dist = 65  # Начальная дистанция группировки
        
        print("--- ЗАГРУЗКА ФАЙЛОВ ---")
        for name, I_val in file_list:
            path = os.path.join(script_dir, name)
            
            if not os.path.exists(path):
                print(f"❌ Файл не найден: {name}")
                continue

            raw_img = cv2.imread(path)
            if raw_img is None: 
                print(f"❌ Ошибка чтения: {name}")
                continue
            gray = raw_img[:,:,2] # Красный канал
            
            processed_img = auto_contrast(gray)
            center = find_center_smart(gray)
            
            self.data.append({
                'name': name, 'I': I_val, 'B': current_to_B(I_val),
                'img_raw': gray, 'img_proc': processed_img,
                'center': center, 'res': None
            })
            print(f"✅ OK: {name} (I={I_val} A)")
            
        if not self.data:
            print("❗ Нет данных. Проверьте список файлов и их наличие в папке.")
            return

        # === НАСТРОЙКА ИНТЕРФЕЙСА ===
        self.fig = plt.figure(figsize=(16, 10), facecolor='#f8f9fa')
        self.fig.canvas.manager.set_window_title('Лабораторная: Эффект Зеемана')
        
        gs = self.fig.add_gridspec(3, 2, height_ratios=[1, 0.8, 0.25], hspace=0.35, wspace=0.2)
        
        self.ax_img = self.fig.add_subplot(gs[0, 0])
        self.ax_prof = self.fig.add_subplot(gs[0, 1])
        self.ax_table = self.fig.add_subplot(gs[1, 0])
        self.ax_final = self.fig.add_subplot(gs[1, 1])
        
        # Панель управления (Sliders & Buttons)
        gs_ctrl = gs[2, :].subgridspec(1, 5, width_ratios=[0.6, 1, 1, 0.8, 0.8], wspace=0.2)
        
        # 1. Режим (Радиокнопки)
        ax_radio = self.fig.add_subplot(gs_ctrl[0])
        ax_radio.set_facecolor('#f8f9fa')
        self.radio = RadioButtons(ax_radio, ('Триплет', 'Дублет'))
        self.radio.on_clicked(self.change_mode)
        for s in ax_radio.spines.values(): s.set_visible(False)
        
        # 2. Слайдеры (Порог, Сглаживание, Группировка)
        ax_sliders = self.fig.add_subplot(gs_ctrl[1])
        ax_sliders.axis('off')
        
        # Слайдер 1: Порог
        sl1 = ax_sliders.inset_axes([0, 0.7, 1, 0.2])
        self.sl_prom = Slider(sl1, 'Порог (Peak) ', 0.5, 20.0, valinit=3.0)
        self.sl_prom.on_changed(self.update_prominence)
        
        # Слайдер 2: Группировка (ВАЖНО ДЛЯ ДУБЛЕТОВ)
        sl2 = ax_sliders.inset_axes([0, 0.4, 1, 0.2])
        self.sl_dist = Slider(sl2, 'Группировка (px) ', 10, 200, valinit=65)
        self.sl_dist.on_changed(self.update_dist)

        # Слайдер 3: Сглаживание
        sl3 = ax_sliders.inset_axes([0, 0.1, 1, 0.2])
        self.sl_smooth = Slider(sl3, 'Сглаживание ', 1, 21, valinit=5, valstep=2)
        self.sl_smooth.on_changed(self.update_smooth)

        # 4. Навигация
        self.btn_prev = Button(self.fig.add_subplot(gs_ctrl[3]), '< Назад')
        self.btn_next = Button(self.fig.add_subplot(gs_ctrl[4]), 'Вперед >')
        self.btn_prev.on_clicked(self.prev_img)
        self.btn_next.on_clicked(self.next_img)
        
        # 5. Кнопка Сохранения
        ax_save = self.fig.add_subplot(gs_ctrl[2])
        ax_save.axis('off')
        btn_sv = ax_save.inset_axes([0.1, 0.3, 0.8, 0.4])
        self.btn_save = Button(btn_sv, '💾 Сохранить отчет', color='#d4edda', hovercolor='#c3e6cb')
        self.btn_save.on_clicked(self.save_report)

        self.recalc_all()
        self.update_view()
        plt.show()

    def recalc_all(self):
        for i in range(len(self.data)): self.process_frame(i)
            
    def process_frame(self, i):
        d = self.data[i]
        raw_prof = get_profile(d['img_proc'], d['center'])
        
        # Сглаживание
        win_len = int(self.smooth_window)
        if win_len < 3: win_len = 3
        if win_len % 2 == 0: win_len += 1
        prof = savgol_filter(raw_prof, win_len, 2)
        
        # 1. Поиск пиков
        peaks_int, _ = find_peaks(prof, prominence=self.prominence, distance=3)
        peaks_sub = np.array([refine_peak(prof, p) for p in peaks_int])
        
        # 2. Группировка (Кластеризация) с учетом текущей настройки distance
        groups = cluster_peaks(peaks_sub, max_distance=self.cluster_dist)
        
        calc_data = []
        deltas_list, Deltas_list = [], []
        
        for k, group in enumerate(groups):
            group = np.array(group)
            r_sq = group**2
            
            delta = 0
            valid = False
            note = ""
            
            # === РЕЖИМ ТРИПЛЕТА ===
            if self.mode == 'triplet':
                if len(group) == 3:
                    # Среднее расщепление
                    d1 = group[1]**2 - group[0]**2
                    d2 = group[2]**2 - group[1]**2
                    delta = (d1 + d2) / 2.0
                    valid = True
                elif len(group) == 2:
                    delta = (group[1]**2 - group[0]**2)
                    valid = False
                    note = "Слиплись"
                else:
                    valid = False
            
            # === РЕЖИМ ДУБЛЕТА ===
            else:
                if len(group) == 2:
                    # В дублете расстояние = 2*deltaE. Делим на 2.
                    delta = (group[1]**2 - group[0]**2) / 2.0
                    valid = True
                elif len(group) == 3:
                    # Иногда шум дает 3 пика в дублете. Берем крайние? 
                    # Нет, лучше пометить как ошибку группировки
                    delta = (group[2]**2 - group[0]**2) / 2.0 # Попытка взять крайние
                    valid = False 
                    note = "Лишний пик"
                else:
                    valid = False
            
            # Расчет Delta (Дисперсионная область)
            Delta = None
            if k < len(groups) - 1:
                curr_mean = np.mean(group**2)
                next_mean = np.mean(np.array(groups[k+1])**2)
                Delta = next_mean - curr_mean

            if valid and Delta is not None:
                # Физическая проверка: расщепление не может быть больше расстояния между порядками
                if delta > Delta * 0.9 or delta <= 0:
                    valid = False
                    note = "Err: d>D"
                else:
                    deltas_list.append(delta)
                    Deltas_list.append(Delta)
            
            calc_data.append({
                'k': k+1, 
                'delta': delta, 
                'Delta': Delta, 
                'valid': valid, 
                'r_peaks': group, 
                'r2': r_sq,
                'note': note
            })
        
        ratio, ratio_err = None, None
        if deltas_list:
            ratios = np.array(deltas_list) / np.array(Deltas_list)
            ratio = np.mean(ratios)
            if len(ratios) > 1:
                ratio_err = np.std(ratios, ddof=1) / np.sqrt(len(ratios))
            else:
                ratio_err = ratio * 0.05
            
        d['res'] = {'peaks': peaks_sub, 'prof': prof, 'raw_prof': raw_prof, 
                    'calc_data': calc_data, 'ratio': ratio, 'ratio_err': ratio_err}

    def update_prominence(self, val):
        self.prominence = val
        self.recalc_all()
        self.update_view()
        
    def update_dist(self, val):
        self.cluster_dist = val
        self.recalc_all()
        self.update_view()
        
    def update_smooth(self, val):
        self.smooth_window = val
        self.recalc_all()
        self.update_view()

    def update_view(self):
        d = self.data[self.idx]
        res = d['res']
        
        # --- 1. КАРТИНКА ---
        self.ax_img.clear()
        self.ax_img.imshow(d['img_proc'], cmap='gray')
        self.ax_img.scatter(*d['center'], c='lime', marker='+', s=120, lw=2)
        self.ax_img.set_title(f"Файл: {d['name']} (I={d['I']} A)", fontsize=11, fontweight='bold')
        self.ax_img.axis('off')
        if res['calc_data']:
            for row in res['calc_data']:
                color = 'lime' if row['valid'] else 'red'
                for r in row['r_peaks']: 
                    self.ax_img.add_patch(plt.Circle(d['center'], r, color=color, fill=False, lw=1))

        # --- 2. ПРОФИЛЬ ---
        self.ax_prof.clear()
        self.ax_prof.plot(res['raw_prof'], color='#ccc', lw=1, alpha=0.5, label='Сырой')
        self.ax_prof.plot(res['prof'], color='#2c3e50', lw=1.5, label='Сглаженный')
        
        if res['calc_data']:
            for row in res['calc_data']:
                if row['valid']:
                    rs = row['r_peaks']
                    y_h = np.max(res['prof'][rs.astype(int)])
                    self.ax_prof.plot(rs, [y_h]*len(rs), 'b-', lw=2)
                    # Вывод дельты над группой
                    lbl_x = np.mean(rs)
                    self.ax_prof.text(lbl_x, y_h*1.05, f"δ={row['delta']:.0f}", color='blue', ha='center', fontsize=8)
        
        self.ax_prof.set_title("Профиль интенсивности", fontsize=10)
        self.ax_prof.legend(fontsize=8)
        self.ax_prof.grid(True, alpha=0.3)

        # --- 3. ТАБЛИЦА ---
        self.ax_table.clear(); self.ax_table.axis('off')
        lines = [f"ДАННЫЕ КАДРА (Режим: {self.mode})"]
        lines.append("-" * 45)
        lines.append(f"{'№':<3}| {'delta':<8}| {'Delta':<8}| {'d/D':<6}")
        lines.append("-" * 45)
        
        if res['calc_data']:
            for row in res['calc_data']:
                d_val = f"{row['delta']:.1f}"
                D_val = f"{row['Delta']:.1f}" if row['Delta'] else "-"
                ratio_val = (row['delta']/row['Delta']) if (row['Delta'] and row['valid']) else 0
                ratio_str = f"{ratio_val:.3f}" if ratio_val else "-"
                
                status = "OK" if row['valid'] else (row['note'] if row['note'] else "❌")
                lines.append(f"{row['k']:<3}| {d_val:<8}| {D_val:<8}| {ratio_str:<6} {status}")
            
            lines.append("-" * 45)
            if res['ratio']:
                err_pct = (res['ratio_err']/res['ratio'])*100
                lines.append(f"СРЕДНЕЕ: {res['ratio']:.4f}")
                lines.append(f"ПОГР:    ±{res['ratio_err']:.4f} ({err_pct:.1f}%)")
            else:
                lines.append("Нет валидных колец")
        else:
            lines.append("ПИКИ НЕ НАЙДЕНЫ")
        
        self.ax_table.text(0.02, 0.98, "\n".join(lines), family='monospace', va='top', fontsize=9.5)

        # --- 4. ГРАФИК ---
        self.draw_final_graph()
        self.fig.canvas.draw_idle()

    def draw_final_graph(self):
        self.ax_final.clear()
        Bs, Rs, Errs = [], [], []
        for item in self.data:
            if item['res'] and item['res']['ratio'] and item['B'] > 0.005:
                Bs.append(item['B']); Rs.append(item['res']['ratio']); Errs.append(item['res']['ratio_err'])
        
        self.ax_final.set_xlabel("Поле B (Тл)"); self.ax_final.set_ylabel("delta / Delta")
        self.ax_final.grid(True, alpha=0.3); self.ax_final.set_title("Определение Магнетона Бора", fontsize=10)
        
        if len(Bs) > 1:
            Bs, Rs, Errs = np.array(Bs), np.array(Rs), np.array(Errs)
            def func(x, m): return m * x
            
            try: popt, pcov = curve_fit(func, Bs, Rs, sigma=Errs, absolute_sigma=True)
            except: popt, pcov = curve_fit(func, Bs, Rs)
            m = popt[0]; m_err = np.sqrt(np.diag(pcov))[0]
            
            mu_calc = m * (h * c) / (2 * d * n_ref)
            mu_err = m_err * (h * c) / (2 * d * n_ref)
            
            err_pct = (mu_err / mu_calc) * 100
            diff_pct = abs(mu_calc - mu_B_theor) / mu_B_theor * 100
            
            self.ax_final.errorbar(Bs, Rs, yerr=Errs, fmt='o', c='k', capsize=3, label='Data')
            x_range = np.linspace(0, max(Bs)*1.1, 50)
            self.ax_final.plot(x_range, func(x_range, m), 'r--', label=f'Fit (m={m:.3f})')
            
            res_txt = (f"$\\mu_B = {mu_calc/1e-24:.2f} \pm {mu_err/1e-24:.2f}$\n($10^{{-24}}$ Дж/Тл)\n"
                       f"Err: {err_pct:.1f}% | Diff: {diff_pct:.1f}%")
            self.ax_final.text(0.95, 0.05, res_txt, transform=self.ax_final.transAxes, ha='right', va='bottom',
                               bbox=dict(facecolor='white', alpha=0.9, boxstyle='round'), fontsize=9)
            self.ax_final.legend(loc='upper left')
            
            curr = self.data[self.idx]
            if curr['res']['ratio']:
                self.ax_final.scatter([curr['B']], [curr['res']['ratio']], s=120, edgecolors='b', facecolors='none', lw=2)
        else:
            self.ax_final.text(0.5, 0.5, "Мало точек", ha='center')

    def save_report(self, event):
        fname = f"zeeman_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(fname, "w", encoding="utf-8") as f:
            f.write("=== ОТЧЕТ ПО ЛАБОРАТОРНОЙ РАБОТЕ: ЭФФЕКТ ЗЕЕМАНА ===\n")
            f.write(f"Дата: {datetime.now()}\n")
            f.write(f"Константы: d={d}м, n={n_ref}\n\n")
            
            Bs, Rs, Errs = [], [], []
            for d_item in self.data:
                f.write(f"--- ФАЙЛ: {d_item['name']} (I={d_item['I']} A, B={d_item['B']:.4f} Тл) ---\n")
                res = d_item['res']
                if not res or not res['calc_data']:
                    f.write("Нет данных.\n\n"); continue
                
                f.write(f"{'Order':<6} {'r_peaks (px)':<30} {'r^2':<30} {'delta':<10} {'Delta':<10} {'Valid'}\n")
                for row in res['calc_data']:
                    r_str = str(np.round(row['r_peaks'], 1))
                    r2_str = str(np.round(row['r2'], 0))
                    valid = "+" if row['valid'] else "-"
                    f.write(f"{row['k']:<6} {r_str:<30} {r2_str:<30} {row['delta']:.2f}      {str(np.round(row['Delta'],2)) if row['Delta'] else '-':<10} {valid}\n")
                
                if res['ratio']:
                    f.write(f"AVG delta/Delta = {res['ratio']:.5f} +/- {res['ratio_err']:.5f}\n")
                    if d_item['B'] > 0.005:
                        Bs.append(d_item['B']); Rs.append(res['ratio']); Errs.append(res['ratio_err'])
                f.write("\n")
            
            f.write("=== ИТОГ ===\n")
            if len(Bs) > 1:
                Bs, Rs, Errs = np.array(Bs), np.array(Rs), np.array(Errs)
                try: popt, pcov = curve_fit(lambda x, m: m*x, Bs, Rs, sigma=Errs, absolute_sigma=True)
                except: popt, pcov = curve_fit(lambda x, m: m*x, Bs, Rs)
                
                m = popt[0]; m_err = np.sqrt(np.diag(pcov))[0]
                mu_calc = m * (h * c) / (2 * d * n_ref)
                mu_err = m_err * (h * c) / (2 * d * n_ref)
                
                f.write(f"Наклон (m): {m:.5f} +/- {m_err:.5f}\n")
                f.write(f"Магнетон Бора: {mu_calc:.4e} +/- {mu_err:.4e} Дж/Тл\n")
                f.write(f"Отклонение: {abs(mu_calc-mu_B_theor)/mu_B_theor*100:.2f}%\n")
            else: f.write("Мало точек.\n")
        print(f"✅ Отчет сохранен: {fname}")

    def on_click(self, event):
        if event.inaxes == self.ax_img:
            self.data[self.idx]['center'] = (int(event.xdata), int(event.ydata))
            self.process_frame(self.idx); self.update_view()
    def change_mode(self, label):
        self.mode = 'triplet' if 'Триплет' in label else 'doublet'
        self.recalc_all(); self.update_view()
    def next_img(self, event):
        self.idx = (self.idx + 1) % len(self.data)
        self.update_view()
    def prev_img(self, event):
        self.idx = (self.idx - 1) % len(self.data)
        self.update_view()

# =========================================================================
# 4. ЗАПУСК
# =========================================================================
if __name__ == "__main__":
    # --- СПИСОК ВАШИХ ФАЙЛОВ ---
    # Проверьте, что они лежат в той же папке!
    files_to_load = [
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
    
    app = LabApp(files_to_load)