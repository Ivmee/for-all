import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, RadioButtons, Slider
from scipy.signal import find_peaks, savgol_filter
from scipy.optimize import curve_fit
import os
from datetime import datetime

# =========================================================================
# 1. ФИЗИЧЕСКИЕ КОНСТАНТЫ (БЕЗ ИЗМЕНЕНИЙ)
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
# 2. АЛГОРИТМЫ ОБРАБОТКИ (БЕЗ ИЗМЕНЕНИЙ)
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
    tbin = np.bincount(r_int.ravel(), img.ravel(), minlength=max_r+1)
    nr = np.bincount(r_int.ravel(), minlength=max_r+1)
    profile = np.zeros_like(tbin, dtype=float)
    mask = nr > 0
    profile[mask] = tbin[mask] / nr[mask]
    return profile

def refine_peak(profile, idx):
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
        
        if dist_from_last < min_dist:
            continue 
            
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
# 3. GUI ПРИЛОЖЕНИЕ (УЛУЧШЕННОЕ)
# =========================================================================
class LabApp:
    def __init__(self, file_list):
        self.data = []
        self.idx = 0
        self.mode = 'triplet' 
        self.smooth_window = 5 
        
        # Начальные значения параметров
        self.prominence = 1.0
        self.min_dist = 2.0
        self.max_dist = 40.0
        
        print("--- ЗАГРУЗКА ФАЙЛОВ ---")
        for name, I_val in file_list:
            path = os.path.join(script_dir, name)
            if not os.path.exists(path):
                print(f"❌ Файл не найден: {name}"); continue

            raw_img = cv2.imread(path)
            if raw_img is None: 
                print(f"❌ Ошибка чтения: {name}"); continue
            gray = raw_img[:,:,2] # Используем красный канал, обычно он контрастнее для лазера
            
            processed_img = auto_contrast(gray)
            center = find_center_smart(gray)
            
            self.data.append({
                'name': name, 'I': I_val, 'B': current_to_B(I_val),
                'img_raw': gray, 'img_proc': processed_img,
                'center': center, 'res': None
            })
            print(f"✅ OK: {name} (I={I_val} A)")
            
        if not self.data: 
            print("Не загружено ни одного файла!")
            return

        # === ИНТЕРФЕЙС ===
        # Используем subplot_adjust чтобы оставить место снизу для контролов
        self.fig = plt.figure(figsize=(16, 9), facecolor='#f0f0f0')
        self.fig.canvas.manager.set_window_title('Лабораторная: Эффект Зеемана v2.0')
        self.fig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.25, hspace=0.3, wspace=0.2)
        
        # Сетка для графиков
        gs = self.fig.add_gridspec(2, 2, height_ratios=[1, 0.8])
        
        self.ax_img = self.fig.add_subplot(gs[0, 0])
        self.ax_prof = self.fig.add_subplot(gs[0, 1])
        self.ax_table = self.fig.add_subplot(gs[1, 0])
        self.ax_final = self.fig.add_subplot(gs[1, 1])
        
        # === ПАНЕЛЬ УПРАВЛЕНИЯ (НИЗ) ===
        # Координаты: [left, bottom, width, height]
        
        # 1. Ползунки (настройки алгоритма)
        ax_sl_prom = plt.axes([0.1, 0.14, 0.35, 0.03])
        ax_sl_max  = plt.axes([0.1, 0.10, 0.35, 0.03])
        ax_sl_min  = plt.axes([0.1, 0.06, 0.35, 0.03])
        ax_sl_sm   = plt.axes([0.1, 0.02, 0.35, 0.03])

        self.sl_prom = Slider(ax_sl_prom, 'Порог (Prom)', 0.1, 10.0, valinit=self.prominence, valfmt='%.1f')
        self.sl_max = Slider(ax_sl_max, 'Макс. расст (Group)', 5.0, 100.0, valinit=self.max_dist, valfmt='%.1f px')
        self.sl_min = Slider(ax_sl_min, 'Мин. расст (Noise)', 0.1, 20.0, valinit=self.min_dist, valfmt='%.1f px')
        self.sl_smooth = Slider(ax_sl_sm, 'Сглаживание', 1, 21, valinit=5, valstep=2, valfmt='%d')

        self.sl_prom.on_changed(self.update_params)
        self.sl_max.on_changed(self.update_params)
        self.sl_min.on_changed(self.update_params)
        self.sl_smooth.on_changed(self.update_params)

        # 2. Навигация и Режим
        ax_prev = plt.axes([0.55, 0.12, 0.08, 0.05])
        ax_next = plt.axes([0.64, 0.12, 0.08, 0.05])
        self.btn_prev = Button(ax_prev, '< Назад')
        self.btn_next = Button(ax_next, 'Вперед >')
        self.btn_prev.on_clicked(self.prev_img)
        self.btn_next.on_clicked(self.next_img)

        ax_radio = plt.axes([0.55, 0.02, 0.17, 0.08], facecolor='#e0e0e0')
        self.radio = RadioButtons(ax_radio, ('Триплет', 'Дублет'))
        self.radio.on_clicked(self.change_mode)

        # 3. Кнопка сохранения
        ax_save = plt.axes([0.80, 0.05, 0.15, 0.10])
        self.btn_save = Button(ax_save, '💾 СОХРАНИТЬ\nОТЧЕТ', color='#d4edda', hovercolor='#c3e6cb')
        self.btn_save.on_clicked(self.save_report)
        
        # Подключаем клик по картинке для ручной центровки
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)

        self.recalc_all()
        self.update_view()
        plt.show()

    def recalc_all(self):
        for i in range(len(self.data)): self.process_frame(i)
            
    def process_frame(self, i):
        d = self.data[i]
        raw_prof = get_profile(d['img_proc'], d['center'])
        
        win_len = int(self.smooth_window)
        if win_len < 3: win_len = 3
        if win_len % 2 == 0: win_len += 1
        prof = savgol_filter(raw_prof, win_len, 2)
        
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
        
        self.ax_final.set_xlabel("Поле B (Тл)"); self.ax_final.set_ylabel("delta / Delta")
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
            
            self.ax_final.errorbar(Bs, Rs, yerr=Errs, fmt='o', c='k', capsize=3, label='Эксп. точки')
            x_range = np.linspace(0, max(Bs)*1.1, 50)
            self.ax_final.plot(x_range, func(x_range, m), 'r--', label=f'Аппроксимация')
            
            res_txt = (f"$\\mu_B = {mu_calc/1e-24:.2f} \pm {mu_err/1e-24:.2f}$ ($10^{{-24}}$ Дж/Тл)\n"
                       f"Погрешность: {err_pct:.1f}%\nОтличие от теории: {diff_pct:.1f}%")
            self.ax_final.text(0.05, 0.95, res_txt, transform=self.ax_final.transAxes, ha='left', va='top',
                               bbox=dict(facecolor='white', alpha=0.9, boxstyle='round'), fontsize=9)
            self.ax_final.legend(loc='lower right', fontsize=8)
            
            curr = self.data[self.idx]
            if curr['res'] and curr['res']['ratio']:
                self.ax_final.scatter([curr['B']], [curr['res']['ratio']], s=150, edgecolors='b', facecolors='none', lw=2)
        else:
            self.ax_final.text(0.5, 0.5, "Недостаточно точек для графика", ha='center')

    def update_view(self):
        d = self.data[self.idx]
        res = d['res']
        
        self.ax_img.clear()
        self.ax_img.imshow(d['img_proc'], cmap='gray')
        self.ax_img.scatter(*d['center'], c='lime', marker='+', s=120, lw=2)
        self.ax_img.set_title(f"Файл: {d['name']} | I={d['I']} A | B={d['B']:.4f} Тл", fontsize=11, fontweight='bold')
        self.ax_img.axis('off')
        
        if res and res['calc_data']:
            for row in res['calc_data']:
                color = 'lime' if row['valid'] else 'red'
                for r in row['r_peaks']: 
                    self.ax_img.add_patch(plt.Circle(d['center'], r, color=color, fill=False, lw=1))

        self.ax_prof.clear()
        if res:
            self.ax_prof.plot(res['raw_prof'], color='#ccc', lw=1, alpha=0.5, label='Сырой сигнал')
            self.ax_prof.plot(res['prof'], color='#2c3e50', lw=1.5, label='Фильтр')
            
            if res['calc_data']:
                for row in res['calc_data']:
                    if row['valid']:
                        rs = row['r_peaks']
                        y_h = np.max(res['prof'][rs.astype(int)])
                        self.ax_prof.plot(rs, [y_h]*len(rs), 'b-', lw=2)
                        lbl_x = np.mean(rs)
                        self.ax_prof.text(lbl_x, y_h*1.05, f"δ={row['delta']:.0f}", color='blue', ha='center', fontsize=8)
        
        self.ax_prof.set_title("Профиль интенсивности", fontsize=10)
        self.ax_prof.legend(fontsize=8)
        self.ax_prof.grid(True, alpha=0.3)

        self.ax_table.clear(); self.ax_table.axis('off')
        lines = [f"РЕЗУЛЬТАТЫ КАДРА ({self.mode.upper()})"]
        lines.append("-" * 55)
        lines.append(f"{'№':<3} {'delta':<10} {'Delta':<10} {'d/D':<8} {'Инфо'}")
        lines.append("-" * 55)
        
        if res and res['calc_data']:
            for row in res['calc_data']:
                d_val = f"{row['delta']:.1f}"
                D_val = f"{row['Delta']:.1f}" if row['Delta'] else "-"
                ratio = (row['delta']/row['Delta']) if (row['Delta'] and row['valid']) else 0
                ratio_str = f"{ratio:.3f}" if ratio > 0 else "-"
                status = "OK" if row['valid'] else (row['note'] if row['note'] else "❌")
                lines.append(f"{row['k']:<3} {d_val:<10} {D_val:<10} {ratio_str:<8} {status}")
            
            lines.append("-" * 55)
            if res['ratio']:
                err_pct = (res['ratio_err']/res['ratio'])*100
                lines.append(f"Среднее d/D: {res['ratio']:.4f} ± {res['ratio_err']:.4f}")
                lines.append(f"Относ. погр: {err_pct:.1f}%")
            else:
                lines.append("Нет валидных колец для расчета")
        else:
            lines.append("Пики не найдены")
        
        self.ax_table.text(0.02, 0.98, "\n".join(lines), family='monospace', va='top', fontsize=10)
        self.draw_final_graph()
        self.fig.canvas.draw_idle()

    def save_report(self, event):
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        fname_txt = f"Zeeman_Report_{timestamp}.txt"
        fname_img = f"Zeeman_Graph_{timestamp}.png"
        
        # Сохранение графика
        self.fig.savefig(fname_img, dpi=100)
        
        # Сохранение текста (Улучшенное форматирование)
        with open(fname_txt, "w", encoding="utf-8") as f:
            f.write("===============================================================\n")
            f.write(f" ЛАБОРАТОРНАЯ РАБОТА: ЭФФЕКТ ЗЕЕМАНА\n")
            f.write(f" Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n")
            f.write("===============================================================\n\n")
            
            f.write("1. ФИЗИЧЕСКИЕ КОНСТАНТЫ\n")
            f.write(f"   Толщина эталона (d):       {d} м\n")
            f.write(f"   Показатель преломления (n): {n_ref}\n")
            f.write(f"   Теоретический магнетон:     {mu_B_theor:.4e} Дж/Тл\n\n")
            
            f.write("2. НАСТРОЙКИ ОБРАБОТКИ\n")
            f.write(f"   Режим: {self.mode}\n")
            f.write(f"   Мин. расстояние между группами (Noise): {self.min_dist:.1f} px\n")
            f.write(f"   Макс. ширина группы (Group):            {self.max_dist:.1f} px\n")
            f.write(f"   Порог обнаружения пика (Prominence):    {self.prominence:.1f}\n\n")
            
            Bs, Rs, Errs = [], [], []
            
            f.write("3. ПОДРОБНЫЕ ДАННЫЕ ПО КАДРАМ\n")
            for d_item in self.data:
                f.write(f"\n   >>> ФАЙЛ: {d_item['name']} (Ток I={d_item['I']} A, Поле B={d_item['B']:.4f} Тл)\n")
                res = d_item['res']
                if not res or not res['calc_data']: 
                    f.write("       [НЕТ ДАННЫХ ДЛЯ ОБРАБОТКИ]\n")
                    continue
                
                # Заголовок таблицы для файла
                header = f"       {'№':<3} | {'r^2 (px^2)':<25} | {'delta':<8} | {'Delta':<8} | {'d/D':<8} | {'Статус'}"
                f.write(header + "\n")
                f.write("       " + "-" * (len(header)) + "\n")
                
                for row in res['calc_data']:
                    r2_str = str(np.round(row['r2'], 0).astype(int))
                    delta_str = f"{row['delta']:.1f}"
                    Delta_str = f"{row['Delta']:.1f}" if row['Delta'] else "-"
                    
                    ratio = row['delta']/row['Delta'] if (row['Delta'] and row['valid']) else 0
                    ratio_str = f"{ratio:.3f}" if ratio > 0 else "-"
                    
                    status = "[ OK ]" if row['valid'] else f"[ERR: {row['note']}]"
                    
                    f.write(f"       {row['k']:<3} | {r2_str:<25} | {delta_str:<8} | {Delta_str:<8} | {ratio_str:<8} | {status}\n")
                
                if res['ratio']:
                    f.write(f"       => СРЕДНЕЕ d/D = {res['ratio']:.5f} +/- {res['ratio_err']:.5f}\n")
                    if d_item['B'] > 0.005:
                        Bs.append(d_item['B'])
                        Rs.append(res['ratio'])
                        Errs.append(res['ratio_err'])
                else:
                    f.write("       => РАСЧЕТ НЕВОЗМОЖЕН\n")

            f.write("\n===============================================================\n")
            f.write("4. ИТОГОВЫЙ РАСЧЕТ (ЛИНЕЙНАЯ РЕГРЕССИЯ)\n")
            f.write("===============================================================\n")
            
            if len(Bs) > 1:
                Bs, Rs, Errs = np.array(Bs), np.array(Rs), np.array(Errs)
                # Линейная аппроксимация y = mx
                try: 
                    popt, pcov = curve_fit(lambda x, m: m*x, Bs, Rs, sigma=Errs, absolute_sigma=True)
                except: 
                    popt, pcov = curve_fit(lambda x, m: m*x, Bs, Rs)
                
                m = popt[0]
                m_err = np.sqrt(np.diag(pcov))[0]
                mu_calc = m * (h * c) / (2 * d * n_ref)
                mu_err = m_err * (h * c) / (2 * d * n_ref)
                
                diff_pct = abs(mu_calc - mu_B_theor) / mu_B_theor * 100
                
                f.write(f"Используемых точек: {len(Bs)}\n")
                f.write(f"Коэффициент наклона прямой (m): {m:.5f} +/- {m_err:.5f} Тл^-1\n\n")
                f.write(f"РЕЗУЛЬТАТ (Эксперимент):     mu_B = {mu_calc:.4e} +/- {mu_err:.4e} Дж/Тл\n")
                f.write(f"                             mu_B = {mu_calc/1e-24:.2f} +/- {mu_err/1e-24:.2f} (* 10^-24)\n\n")
                f.write(f"ТЕОРЕТИЧЕСКОЕ ЗНАЧЕНИЕ:      mu_B = {mu_B_theor:.4e} Дж/Тл\n")
                f.write(f"ОТКЛОНЕНИЕ ОТ ТЕОРИИ:        {diff_pct:.2f} %\n")
            else:
                f.write("Недостаточно валидных точек для построения графика.\n")
                
        print(f"✅ Отчет сохранен: {fname_txt}")
        print(f"✅ График сохранен: {fname_img}")

    def on_click(self, event):
        # Если клик был внутри картинки, обновляем центр вручную
        if event.inaxes == self.ax_img:
            if event.xdata is not None and event.ydata is not None:
                print(f"Ручная установка центра: {int(event.xdata)}, {int(event.ydata)}")
                self.data[self.idx]['center'] = (int(event.xdata), int(event.ydata))
                self.process_frame(self.idx)
                self.update_view()
    
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
    # Список файлов должен лежать в той же папке
    files_to_load = [
        ("0,5.jpg", 0.5), ("0,8.jpg", 0.8), ("1,1.jpg", 1.1),
        ("1,3.jpg", 1.3), ("1,5.jpg", 1.5), ("1,7.jpg", 1.7),
        ("1,9.jpg", 1.9), ("2,1.jpg", 2.1), ("2,3.jpg", 2.3), ("2,5.jpg", 2.5)
    ]
    app = LabApp(files_to_load)