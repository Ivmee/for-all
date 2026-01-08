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
    return np.interp(I, CALIB_I, CALIB_B_mT) / 1000.0

# =========================================================================
# 2. АЛГОРИТМЫ ОБРАБОТКИ
# =========================================================================

def auto_contrast(img_gray):
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    return clahe.apply(img_gray)

def find_center_smart(img_gray):
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
    cX, cY = center
    Y, X = np.ogrid[:img.shape[0], :img.shape[1]]
    r_map = np.sqrt((X - cX)**2 + (Y - cY)**2)
    r_int = r_map.astype(int)
    max_r = int(np.max(r_int))
    
    # Используем быстрый bincount для суммирования
    tbin = np.bincount(r_int.ravel(), img.ravel(), minlength=max_r+1)
    nr = np.bincount(r_int.ravel(), minlength=max_r+1)
    
    profile = np.zeros_like(tbin, dtype=float)
    mask = nr > 0
    profile[mask] = tbin[mask] / nr[mask]
    return profile

def refine_peak(profile, idx):
    """ Параболическая интерполяция для уточнения вершины пика """
    if idx <= 0 or idx >= len(profile) - 1: return idx
    y1, y2, y3 = float(profile[idx-1]), float(profile[idx]), float(profile[idx+1])
    denom = y1 - 2*y2 + y3
    if denom == 0: return idx
    return idx + (y1 - y3) / (2*denom)

def cluster_peaks(peaks, min_dist=5, max_dist=60):
    if len(peaks) == 0: return []
    groups = []
    current_group = [peaks[0]]
    last_valid_peak = peaks[0]
    
    for i in range(1, len(peaks)):
        curr = peaks[i]
        dist_from_last = curr - last_valid_peak
        
        # Фильтр совсем близких пиков (шум)
        if dist_from_last < min_dist:
            continue 
            
        # Если пик далеко от текущей группы — начинаем новую
        if curr - current_group[-1] < max_dist:
            current_group.append(curr)
            last_valid_peak = curr
        else:
            groups.append(current_group)
            current_group = [curr]
            last_valid_peak = curr
            
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
        
        # Начальные параметры
        self.smooth_window = 5 
        self.prominence = 2.0
        self.min_dist = 3.0
        self.max_dist = 40.0
        
        print("--- ЗАГРУЗКА ФАЙЛОВ ---")
        for name, I_val in file_list:
            path = os.path.join(script_dir, name)
            if not os.path.exists(path):
                print(f"❌ Файл не найден: {name} (пропускаем)"); continue

            raw_img = cv2.imread(path)
            if raw_img is None: 
                print(f"❌ Ошибка чтения: {name}"); continue
            
            # Берем красный канал (обычно самый контрастный для лазера/лампы)
            gray = raw_img[:,:,2]
            processed_img = auto_contrast(gray)
            center = find_center_smart(gray)
            
            self.data.append({
                'name': name, 'I': I_val, 'B': current_to_B(I_val),
                'img_raw': gray, 'img_proc': processed_img,
                'center': center, 'res': None
            })
            print(f"✅ OK: {name} (I={I_val} A)")
            
        if not self.data:
            print("Не удалось загрузить ни одного файла.")
            return

        # === НАСТРОЙКА ИНТЕРФЕЙСА ===
        self.fig = plt.figure(figsize=(15, 9), facecolor='#f0f0f0')
        self.fig.canvas.manager.set_window_title('Лабораторная: Эффект Зеемана')
        
        # Сетка: 2 строки графиков + 1 строка управления внизу
        gs = self.fig.add_gridspec(3, 2, height_ratios=[1, 1, 0.4], hspace=0.3, wspace=0.2)
        
        self.ax_img = self.fig.add_subplot(gs[0, 0])
        self.ax_prof = self.fig.add_subplot(gs[0, 1])
        self.ax_table = self.fig.add_subplot(gs[1, 0])
        self.ax_final = self.fig.add_subplot(gs[1, 1])
        
        # Подключаем клик мыши для ручного центра
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.on_click)

        # === ПАНЕЛЬ УПРАВЛЕНИЯ (Слайдеры и кнопки) ===
        # Делим нижнюю часть на зоны
        gs_ctrl = gs[2, :].subgridspec(1, 3, width_ratios=[0.2, 0.5, 0.3])
        
        # 1. Левая зона: Режим и Сохранение
        gs_left = gs_ctrl[0].subgridspec(3, 1)
        
        ax_radio = self.fig.add_subplot(gs_left[0:2])
        ax_radio.set_facecolor('#f0f0f0')
        self.radio = RadioButtons(ax_radio, ('Триплет', 'Дублет'))
        self.radio.on_clicked(self.change_mode)
        
        self.btn_save = Button(self.fig.add_subplot(gs_left[2]), '💾 Сохранить TXT', color='#28a745', hovercolor='#218838')
        self.btn_save.label.set_color('white')
        self.btn_save.on_clicked(self.save_report)

        # 2. Средняя зона: Слайдеры (Сделаем их побольше)
        gs_sliders = gs_ctrl[1].subgridspec(4, 1, hspace=0.5)
        
        self.sl_max = Slider(self.fig.add_subplot(gs_sliders[0]), 'Max Dist (Группа)', 
                             10.0, 150.0, valinit=self.max_dist, valfmt='%0.1f px')
        self.sl_max.on_changed(self.update_params)

        self.sl_min = Slider(self.fig.add_subplot(gs_sliders[1]), 'Min Dist (Шум)', 
                             0.5, 30.0, valinit=self.min_dist, valfmt='%0.1f px')
        self.sl_min.on_changed(self.update_params)
        
        self.sl_prom = Slider(self.fig.add_subplot(gs_sliders[2]), 'Порог Пика', 
                              0.1, 20.0, valinit=self.prominence, valfmt='%0.1f')
        self.sl_prom.on_changed(self.update_params)

        self.sl_smooth = Slider(self.fig.add_subplot(gs_sliders[3]), 'Сглаживание', 
                                1, 31, valinit=self.smooth_window, valstep=2, valfmt='%d')
        self.sl_smooth.on_changed(self.update_params)

        # 3. Правая зона: Навигация
        gs_nav = gs_ctrl[2].subgridspec(1, 2, wspace=0.1)
        self.btn_prev = Button(self.fig.add_subplot(gs_nav[0]), '< Назад')
        self.btn_next = Button(self.fig.add_subplot(gs_nav[1]), 'Вперед >')
        self.btn_prev.on_clicked(self.prev_img)
        self.btn_next.on_clicked(self.next_img)
        
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
        try:
            prof = savgol_filter(raw_prof, win_len, 2)
        except:
            prof = raw_prof # Fallback

        # Поиск пиков
        peaks_int, _ = find_peaks(prof, prominence=self.prominence, distance=max(1, int(self.min_dist/2)))
        peaks_sub = np.array([refine_peak(prof, p) for p in peaks_int])
        
        groups = cluster_peaks(peaks_sub, min_dist=self.min_dist, max_dist=self.max_dist)
        
        calc_data = []
        deltas_list, Deltas_list = [], []
        
        for k, group in enumerate(groups):
            group = np.array(group)
            r_sq = group**2
            
            delta = 0
            valid = False
            note = ""
            
            # --- ТРИПЛЕТ ---
            if self.mode == 'triplet':
                if len(group) == 3:
                    d1 = group[1]**2 - group[0]**2
                    d2 = group[2]**2 - group[1]**2
                    delta = (d1 + d2) / 2.0
                    valid = True
                elif len(group) == 2:
                    delta = (group[1]**2 - group[0]**2)
                    valid = False
                    note = "Слиплись (2)"
                else:
                    note = f"{len(group)} пика"
            
            # --- ДУБЛЕТ ---
            else:
                if len(group) == 2:
                    delta = (group[1]**2 - group[0]**2) / 2.0
                    valid = True
                elif len(group) > 2:
                    delta = (group[-1]**2 - group[0]**2) / 2.0
                    valid = False
                    note = "Лишний пик"
                else:
                    note = f"{len(group)} пика"

            Delta = None
            if k < len(groups) - 1:
                curr_mean = np.mean(group**2)
                next_mean = np.mean(np.array(groups[k+1])**2)
                Delta = next_mean - curr_mean

            if valid and Delta is not None:
                if delta > Delta * 0.9 or delta <= 0:
                    valid = False
                    note = "Err: d>D"
                else:
                    deltas_list.append(delta)
                    Deltas_list.append(Delta)
            
            calc_data.append({
                'k': k+1, 'delta': delta, 'Delta': Delta, 
                'valid': valid, 'r_peaks': group, 'r2': r_sq, 'note': note
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

    def update_params(self, val):
        self.prominence = self.sl_prom.val
        self.smooth_window = self.sl_smooth.val
        self.min_dist = self.sl_min.val
        self.max_dist = self.sl_max.val
        self.recalc_all()
        self.update_view()

    def draw_final_graph(self):
        self.ax_final.clear()
        Bs, Rs, Errs = [], [], []
        for item in self.data:
            if item['res'] and item['res']['ratio'] and item['B'] > 0.005:
                Bs.append(item['B']); Rs.append(item['res']['ratio']); Errs.append(item['res']['ratio_err'])
        
        self.ax_final.set_xlabel("Поле B (Тл)")
        self.ax_final.set_ylabel(r"$\delta / \Delta$")
        self.ax_final.grid(True, alpha=0.3)
        self.ax_final.set_title("Определение Магнетона Бора", fontsize=10)
        
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
            
            self.ax_final.errorbar(Bs, Rs, yerr=Errs, fmt='o', c='k', capsize=3, markersize=4)
            x_range = np.linspace(0, max(Bs)*1.1, 50)
            self.ax_final.plot(x_range, func(x_range, m), 'r--', label=f'Fit')
            
            res_txt = (f"$\\mu_B = {mu_calc/1e-24:.2f} \pm {mu_err/1e-24:.2f}$ ($10^{{-24}}$)\n"
                       f"Diff: {diff_pct:.1f}%")
            self.ax_final.text(0.05, 0.95, res_txt, transform=self.ax_final.transAxes, ha='left', va='top',
                               bbox=dict(facecolor='white', alpha=0.9, boxstyle='round'), fontsize=9)
            
            # Подсветка текущей точки
            curr = self.data[self.idx]
            if curr['res'] and curr['res']['ratio']:
                self.ax_final.plot([curr['B']], [curr['res']['ratio']], 'bo', markersize=10, markerfacecolor='none', markeredgewidth=2)
        else:
            self.ax_final.text(0.5, 0.5, "Мало точек", ha='center')

    def update_view(self):
        d = self.data[self.idx]
        res = d['res']
        
        # 1. Image
        self.ax_img.clear()
        self.ax_img.imshow(d['img_proc'], cmap='gray')
        self.ax_img.scatter(*d['center'], c='lime', marker='+', s=100, lw=1.5)
        self.ax_img.set_title(f"Файл: {d['name']} (I={d['I']} A)", fontsize=10, fontweight='bold')
        self.ax_img.axis('off')
        
        if res and res['calc_data']:
            for row in res['calc_data']:
                color = 'lime' if row['valid'] else 'red'
                for r in row['r_peaks']: 
                    self.ax_img.add_patch(plt.Circle(d['center'], r, color=color, fill=False, lw=1))

        # 2. Profile
        self.ax_prof.clear()
        if res:
            self.ax_prof.plot(res['raw_prof'], color='#ccc', lw=1, alpha=0.5)
            self.ax_prof.plot(res['prof'], color='#2c3e50', lw=1.5)
            
            if res['calc_data']:
                for row in res['calc_data']:
                    if row['valid']:
                        rs = row['r_peaks']
                        y_h = np.max(res['prof'][rs.astype(int)])
                        self.ax_prof.plot(rs, [y_h]*len(rs), 'b-', lw=2)
                        lbl_x = np.mean(rs)
                        self.ax_prof.text(lbl_x, y_h*1.05, f"δ={row['delta']:.0f}", color='blue', ha='center', fontsize=8)
        
        self.ax_prof.set_title("Профиль интенсивности", fontsize=10)
        self.ax_prof.grid(True, alpha=0.3)

        # 3. Table
        self.ax_table.clear(); self.ax_table.axis('off')
        lines = [f"ДАННЫЕ ({self.mode})"]
        lines.append(f"{'k':<3} | {'delta':<8} | {'Delta':<8} | {'d/D':<6}")
        lines.append("-" * 40)
        
        if res and res['calc_data']:
            for row in res['calc_data']:
                d_val = f"{row['delta']:.1f}"
                D_val = f"{row['Delta']:.1f}" if row['Delta'] else "-"
                ratio_val = (row['delta']/row['Delta']) if (row['Delta'] and row['valid']) else 0
                ratio_str = f"{ratio_val:.3f}" if ratio_val else "-"
                status = "" if row['valid'] else " (x)"
                lines.append(f"{row['k']:<3} | {d_val:<8} | {D_val:<8} | {ratio_str:<6}{status}")
            
            lines.append("-" * 40)
            if res['ratio']:
                lines.append(f"СРЕДНЕЕ: {res['ratio']:.4f}")
                lines.append(f"ПОГР:    ±{res['ratio_err']:.4f}")
            else:
                lines.append("Нет валидных колец")
        else:
            lines.append("Нет данных")
        
        self.ax_table.text(0.0, 1.0, "\n".join(lines), family='monospace', va='top', fontsize=10)
        self.draw_final_graph()
        self.fig.canvas.draw_idle()

    def save_report(self, event):
        fname = f"zeeman_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            with open(fname, "w", encoding="utf-8") as f:
                # ЗАГОЛОВОК
                f.write("="*80 + "\n")
                f.write(f"ОТЧЕТ ПО ЛАБОРАТОРНОЙ РАБОТЕ: ЭФФЕКТ ЗЕЕМАНА\n")
                f.write(f"Дата создания: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n")
                f.write("="*80 + "\n\n")
                
                f.write("1. ПАРАМЕТРЫ УСТАНОВКИ\n")
                f.write(f"   Толщина эталона (d):   {d:.2e} м\n")
                f.write(f"   Пок-ль преломления (n): {n_ref}\n")
                f.write(f"   Режим обработки:       {self.mode}\n")
                f.write("-" * 80 + "\n\n")

                Bs, Rs, Errs = [], [], []

                # ПОКАДРОВЫЙ ОТЧЕТ
                f.write("2. ДАННЫЕ ПО ИЗОБРАЖЕНИЯМ\n")
                for d_item in self.data:
                    res = d_item['res']
                    f.write(f"\n>>> ФАЙЛ: {d_item['name']}\n")
                    f.write(f"    Ток I = {d_item['I']} A  ==>  Поле B = {d_item['B']:.4f} Тл\n")
                    
                    if not res or not res['calc_data']:
                        f.write("    [НЕТ ДАННЫХ]\n")
                        continue

                    # Таблица для кадра
                    # Форматирование: ширина полей фиксирована
                    header = f"    {'№':<3} | {'R (px)':<20} | {'R^2 (px^2)':<20} | {'delta':<8} | {'Delta':<8} | {'ratio':<6} | {'Status'}"
                    f.write(header + "\n")
                    f.write("    " + "-" * (len(header)-4) + "\n")
                    
                    for row in res['calc_data']:
                        r_str = str(np.round(row['r_peaks'], 1).tolist())
                        r2_str = str(np.round(row['r2'], 0).tolist())
                        delta_s = f"{row['delta']:.1f}"
                        Delta_s = f"{row['Delta']:.1f}" if row['Delta'] else "-"
                        
                        ratio = row['delta']/row['Delta'] if (row['Delta'] and row['valid']) else 0
                        ratio_s = f"{ratio:.3f}" if ratio > 0 else "-"
                        mark = "[OK]" if row['valid'] else f"[ERR: {row['note']}]"
                        
                        f.write(f"    {row['k']:<3} | {r_str:<20} | {r2_str:<20} | {delta_s:<8} | {Delta_s:<8} | {ratio_s:<6} | {mark}\n")

                    if res['ratio']:
                        f.write(f"    ---> Среднее ratio: {res['ratio']:.5f} ± {res['ratio_err']:.5f}\n")
                        if d_item['B'] > 0.005:
                            Bs.append(d_item['B'])
                            Rs.append(res['ratio'])
                            Errs.append(res['ratio_err'])
                    else:
                        f.write("    ---> Недостаточно данных для расчета среднего\n")

                # ИТОГОВЫЙ РАСЧЕТ
                f.write("\n" + "="*80 + "\n")
                f.write("3. ИТОГОВЫЙ РЕЗУЛЬТАТ (МНК)\n")
                if len(Bs) > 1:
                    Bs_arr, Rs_arr, Errs_arr = np.array(Bs), np.array(Rs), np.array(Errs)
                    try:
                        popt, pcov = curve_fit(lambda x, m: m*x, Bs_arr, Rs_arr, sigma=Errs_arr, absolute_sigma=True)
                    except:
                        popt, pcov = curve_fit(lambda x, m: m*x, Bs_arr, Rs_arr)
                    
                    m = popt[0]
                    m_err = np.sqrt(np.diag(pcov))[0]
                    
                    mu_calc = m * (h * c) / (2 * d * n_ref)
                    mu_err = m_err * (h * c) / (2 * d * n_ref)
                    diff_pct = abs(mu_calc - mu_B_theor) / mu_B_theor * 100
                    
                    f.write(f"Найдено точек для графика: {len(Bs)}\n")
                    f.write(f"Наклон прямой (m):         {m:.5f} ± {m_err:.5f}\n")
                    f.write("-" * 40 + "\n")
                    f.write(f"МАГНЕТОН БОРА (mu_B):\n")
                    f.write(f"   Эксперимент:  {mu_calc:.4e} ± {mu_err:.4e} Дж/Тл\n")
                    f.write(f"   Теория:       {mu_B_theor:.4e} Дж/Тл\n")
                    f.write(f"   Отклонение:   {diff_pct:.2f} %\n")
                else:
                    f.write("Недостаточно точек для построения графика и расчета mu_B.\n")
                f.write("="*80 + "\n")
            
            print(f"✅ Отчет успешно сохранен: {fname}")
        except Exception as e:
            print(f"❌ Ошибка сохранения: {e}")

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

if __name__ == "__main__":
    # Убедитесь, что файлы лежат в папке скрипта или укажите полные пути
    files_to_load = [
        ("0,5.jpg", 0.5), ("0,8.jpg", 0.8), ("1,1.jpg", 1.1),
        ("1,3.jpg", 1.3), ("1,5.jpg", 1.5), ("1,7.jpg", 1.7),
        ("1,9.jpg", 1.9), ("2,1.jpg", 2.1), ("2,3.jpg", 2.3), ("2,5.jpg", 2.5)
    ]
    app = LabApp(files_to_load)