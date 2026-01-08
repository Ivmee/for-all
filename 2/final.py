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


# 2. АЛГОРИТМЫ ОБРАБОТКИ


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


# ================================
# 3. GUI ПРИЛОЖЕНИЕ 
# =================================
class LabApp:
    def __init__(self, file_list):
        self.data = []
        self.idx = 0
        self.mode = 'triplet' 
        
        # --- Параметры ---
        self.prominence = 3.0 
        self.smooth_window = 5 
        self.min_width_px = 2.0   
        self.max_width_px = 30.0  
        
        # НОВЫЕ ПАРАМЕТРЫ (Ограничение радиуса)
        self.r_min_cutoff = 0
        self.r_max_cutoff = 500 # Дефолтное значение,

        print("--- ЗАГРУЗКА ФАЙЛОВ ---")
        for name, I_val in file_list:
            path = os.path.join(script_dir, name)
            if not os.path.exists(path):
                print(f"Файл не найден: {name}")
                continue
            raw_img = cv2.imread(path)
            if raw_img is None: continue
            gray = raw_img[:,:,2] 
            processed_img = auto_contrast(gray)
            center = find_center_smart(gray)
            
            # Обновим дефолтный макс радиус по размеру картинки
            diag = int(np.sqrt((gray.shape[0]/2)**2 + (gray.shape[1]/2)**2))
            if diag > self.r_max_cutoff: self.r_max_cutoff = diag

            self.data.append({
                'name': name, 'I': I_val, 'B': current_to_B(I_val),
                'img_raw': gray, 'img_proc': processed_img,
                'center': center, 'res': None
            })
            print(f"✅ OK: {name}")
            
        if not self.data: return

        # === GUI ===
        self.fig = plt.figure(figsize=(16, 10), facecolor='#f8f9fa')
        self.fig.canvas.manager.set_window_title('Лабораторная: Зееман + Фильтр радиуса')
        
        gs = self.fig.add_gridspec(3, 2, height_ratios=[1, 0.8, 0.45], hspace=0.4, wspace=0.2)
        
        self.ax_img = self.fig.add_subplot(gs[0, 0])
        self.ax_prof = self.fig.add_subplot(gs[0, 1])
        self.ax_table = self.fig.add_subplot(gs[1, 0])
        self.ax_final = self.fig.add_subplot(gs[1, 1])
        
        # Панель управления
        gs_ctrl = gs[2, :].subgridspec(1, 4, width_ratios=[0.5, 1.2, 0.8, 0.8], wspace=0.2)
        
        # 1. кнопки
        ax_radio = self.fig.add_subplot(gs_ctrl[0])
        ax_radio.set_facecolor('#f8f9fa')
        self.radio = RadioButtons(ax_radio, ('Триплет', 'Дублет'))
        self.radio.on_clicked(self.change_mode)
        for s in ax_radio.spines.values(): s.set_visible(False)
        
        # 2. Слайдеры 
        ax_sliders_container = self.fig.add_subplot(gs_ctrl[1])
        ax_sliders_container.axis('off')
        
        
        sh = 0.10 # Высота
        gap = 0.04 # Отступ
        
        # Функция создания слайдера
        def make_slider(pos_idx, label, vmin, vmax, vinit):
            ax = ax_sliders_container.inset_axes([0, pos_idx*(sh+gap), 1, sh])
            return Slider(ax, label, vmin, vmax, valinit=vinit)

        self.sl_prom = make_slider(5, 'Порог (ампл)', 0.5, 50.0, 3.0)
        self.sl_smooth = make_slider(4, 'Сглаживание', 1, 21, 5)
        self.sl_min_w = make_slider(3, 'Мин. ширина дуп.', 1.0, 20.0, self.min_width_px)
        self.sl_max_w = make_slider(2, 'Макс. ширина дуп.', 5.0, 150.0, self.max_width_px)
        
        # Новые слайдеры радиуса
        self.sl_rmin = make_slider(1, 'R мин (px)', 0, 300, 0)
        self.sl_rmax = make_slider(0, 'R макс (px)', 100, self.r_max_cutoff, self.r_max_cutoff)
        
        for sl in [self.sl_prom, self.sl_smooth, self.sl_min_w, self.sl_max_w, self.sl_rmin, self.sl_rmax]:
            sl.on_changed(self.update_params)

        # 3. Сохранение
        ax_save = self.fig.add_subplot(gs_ctrl[2])
        ax_save.axis('off')
        btn_sv = ax_save.inset_axes([0.1, 0.4, 0.8, 0.3])
        self.btn_save = Button(btn_sv, 'Сохранить отчет', color='#d4edda')
        self.btn_save.on_clicked(self.save_report)
        
        # 4. Навигация
        gs_nav = gs_ctrl[3].subgridspec(2, 1, hspace=0.1)
        self.btn_prev = Button(self.fig.add_subplot(gs_nav[0]), '< Назад')
        self.btn_next = Button(self.fig.add_subplot(gs_nav[1]), 'Вперед >')
        self.btn_prev.on_clicked(self.prev_img)
        self.btn_next.on_clicked(self.next_img)

        self.fig.canvas.mpl_connect('button_press_event', self.on_click)

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
        peaks_int, _ = find_peaks(prof, prominence=self.prominence, distance=2) 
        
        # Фильтрация по радиусу ===
        # Оставляем только те пики, что внутри [r_min, r_max]
        if len(peaks_int) > 0:
            mask = (peaks_int >= self.r_min_cutoff) & (peaks_int <= self.r_max_cutoff)
            peaks_int = peaks_int[mask]

        # 2. Группировка 
        valid_groups = []
        used_indices = set()
        comps = 3 if self.mode == 'triplet' else 2
        
        peaks_sorted = np.sort(peaks_int)
        
        for p_idx in range(len(peaks_sorted) - (comps - 1)):
            if p_idx in used_indices: continue
            
            candidate_group = [peaks_sorted[p_idx]]
            is_good_group = True
            current_idx = p_idx
            
            for k in range(comps - 1):
                next_peak_idx = current_idx + 1
                if next_peak_idx >= len(peaks_sorted):
                    is_good_group = False; break
                
                dist = peaks_sorted[next_peak_idx] - peaks_sorted[current_idx]
                if self.min_width_px <= dist <= self.max_width_px:
                    candidate_group.append(peaks_sorted[next_peak_idx])
                    current_idx = next_peak_idx
                else:
                    is_good_group = False; break
            
            if is_good_group:
                valid_groups.append(np.array(candidate_group))
                for j in range(comps): used_indices.add(p_idx + j)
        
        # 3. Расчет
        calc_data = []
        deltas, Deltas = [], []
        
        for k, group_int in enumerate(valid_groups):
            group_sub = np.array([refine_peak(prof, p) for p in group_int])
            r_sq = group_sub**2
            delta, Delta = 0, None
            
            if self.mode == 'triplet':
                delta = ((r_sq[1]-r_sq[0]) + (r_sq[2]-r_sq[1])) / 2.0
                if k < len(valid_groups) - 1:
                    next_group = np.array([refine_peak(prof, p) for p in valid_groups[k+1]])
                    Delta = next_group[1]**2 - r_sq[1]
            else: 
                delta = (r_sq[1] - r_sq[0]) / 2.0
                if k < len(valid_groups) - 1:
                    next_group = np.array([refine_peak(prof, p) for p in valid_groups[k+1]])
                    Delta = np.mean(next_group**2) - np.mean(r_sq)
            
            valid_row = True
            if Delta is not None:
                if delta > Delta * 0.9: valid_row = False 
                else: deltas.append(delta); Deltas.append(Delta)
            
            calc_data.append({
                'k': k+1, 'delta': delta, 'Delta': Delta, 
                'valid': valid_row and (Delta is not None), 
                'r_peaks': group_sub
            })
            
        ratio, ratio_err = None, None
        if deltas and Deltas:
            mean_d, mean_D = np.mean(deltas), np.mean(Deltas)
            if mean_d > 0 and mean_D > 0:
                sem_d = np.std(deltas, ddof=1)/np.sqrt(len(deltas)) if len(deltas)>1 else mean_d*0.05
                sem_D = np.std(Deltas, ddof=1)/np.sqrt(len(Deltas)) if len(Deltas)>1 else mean_D*0.05
                ratio = mean_d / mean_D
                ratio_err = ratio * np.sqrt((sem_d/mean_d)**2 + (sem_D/mean_D)**2)
            
        d['res'] = {'prof': prof, 'raw_prof': raw_prof, 'calc_data': calc_data, 
                    'ratio': ratio, 'ratio_err': ratio_err}

    def update_params(self, val):
        self.prominence = self.sl_prom.val
        self.smooth_window = self.sl_smooth.val
        self.min_width_px = self.sl_min_w.val
        self.max_width_px = self.sl_max_w.val
        self.r_min_cutoff = self.sl_rmin.val
        self.r_max_cutoff = self.sl_rmax.val
        self.recalc_all()
        self.update_view()

    def update_view(self):
        d = self.data[self.idx]
        res = d['res']
        if res is None: return

        # --- КАРТИНКА ---
        self.ax_img.clear()
        self.ax_img.imshow(d['img_proc'], cmap='gray')
        self.ax_img.scatter(*d['center'], c='lime', marker='+', s=120)
        self.ax_img.set_title(f"Файл: {d['name']} (I={d['I']} A)", fontsize=11)
        self.ax_img.axis('off')
        
        # Рисуем круги отсечения на картинке для наглядности
        self.ax_img.add_patch(plt.Circle(d['center'], self.r_min_cutoff, color='red', fill=False, ls='--', alpha=0.5))
        self.ax_img.add_patch(plt.Circle(d['center'], self.r_max_cutoff, color='red', fill=False, ls='--', alpha=0.5))

        if res['calc_data']:
            for row in res['calc_data']:
                color = 'lime' if row['valid'] else 'red'
                for r in row['r_peaks']: 
                    self.ax_img.add_patch(plt.Circle(d['center'], r, color=color, fill=False, lw=1))

        # --- ПРОФИЛЬ ---
        self.ax_prof.clear()
        self.ax_prof.plot(res['raw_prof'], color='#ccc', lw=1, alpha=0.5)
        self.ax_prof.plot(res['prof'], color='#2c3e50', lw=1.5)
        
        # Затемняем отсеченные зоны
        ymax = np.max(res['prof']) * 1.1
        self.ax_prof.fill_betweenx([0, ymax], 0, self.r_min_cutoff, color='red', alpha=0.1, label='Cutoff')
        self.ax_prof.fill_betweenx([0, ymax], self.r_max_cutoff, len(res['prof']), color='red', alpha=0.1)
        
        if res['calc_data']:
            for row in res['calc_data']:
                rs = row['r_peaks']
                y_h = np.max(res['prof'][rs.astype(int).clip(0, len(res['prof'])-1)])
                self.ax_prof.plot(rs, [y_h]*len(rs), color='blue' if row['valid'] else 'red', lw=2)
                mid_r = np.mean(rs)
                self.ax_prof.text(mid_r, y_h*1.02, f"δ={row['delta']:.0f}", color='blue', ha='center', fontsize=8, rotation=90)
        
        self.ax_prof.set_title("Профиль (Красным — исключенные зоны)")
        self.ax_prof.set_xlim(0, len(res['prof']))

        # --- ТАБЛИЦА ---
        self.ax_table.clear(); self.ax_table.axis('off')
        lines = [f"Параметры R: [{int(self.r_min_cutoff)} ... {int(self.r_max_cutoff)}] px"]
        lines.append("-" * 45)
        lines.append(f"{'№':<3}| {'r (px)':<12}| {'delta':<8}| {'Delta':<8}")
        lines.append("-" * 45)
        
        if res['calc_data']:
            for row in res['calc_data']:
                r_str = ",".join([f"{x:.0f}" for x in row['r_peaks']])
                d_val = f"{row['delta']:.0f}"
                D_val = f"{row['Delta']:.0f}" if row['Delta'] else "-"
                mark = " " if row['valid'] else "❌"
                lines.append(f"{row['k']:<3}| {r_str:<12}| {d_val:<8}| {D_val:<8} {mark}")
            if res['ratio']: lines.append(f"\nAVG ratio: {res['ratio']:.4f}")
        else: lines.append("Нет данных в выбранном диапазоне")
        self.ax_table.text(0.02, 0.98, "\n".join(lines), family='monospace', va='top', fontsize=9)

        # --- ГРАФИК ---
        self.draw_final_graph()
        self.fig.canvas.draw_idle()

    def draw_final_graph(self):
        self.ax_final.clear()
        Bs, Rs, Errs = [], [], []
        for item in self.data:
            if item['res'] and item['res']['ratio'] and item['B'] > 0.005:
                Bs.append(item['B']); Rs.append(item['res']['ratio']); Errs.append(item['res']['ratio_err'] or 0.01)
        
        self.ax_final.set_xlabel("B (Тл)"); self.ax_final.set_ylabel("delta / Delta")
        self.ax_final.grid(True, alpha=0.3)
        if len(Bs) > 1:
            def func(x, m): return m * x
            try: popt, pcov = curve_fit(func, Bs, Rs, sigma=Errs, absolute_sigma=True)
            except: popt, pcov = curve_fit(func, Bs, Rs)
            m = popt[0]
            mu_calc = m * (h * c) / (2 * d * n_ref)
            self.ax_final.errorbar(Bs, Rs, yerr=Errs, fmt='o', c='k', capsize=3)
            self.ax_final.plot(np.linspace(0, max(Bs)*1.1), func(np.linspace(0, max(Bs)*1.1), m), 'r--')
            self.ax_final.text(0.05, 0.95, f"$\\mu_B \\approx {mu_calc/((1e-24)*2):.2f} \\times 10^{{-24}}$", 
                               transform=self.ax_final.transAxes, va='top', bbox=dict(facecolor='white', alpha=0.8))
            curr = self.data[self.idx]
            if curr['res'] and curr['res']['ratio']:
                self.ax_final.scatter([curr['B']], [curr['res']['ratio']], s=150, edgecolors='b', facecolors='none', lw=2)

    def save_report(self, event):
        fname = f"zeeman_report_{datetime.now().strftime('%H%M%S')}.txt"
        with open(fname, "w", encoding="utf-8") as f:
            f.write(f"REPORT {datetime.now()}\nParams: R_min={self.r_min_cutoff}, R_max={self.r_max_cutoff}\n")
            for d_item in self.data:
                f.write(f"\nFILE: {d_item['name']} (B={d_item['B']:.3f})\n")
                if d_item['res'] and d_item['res']['calc_data']:
                    for row in d_item['res']['calc_data']:
                        f.write(f"  Order {row['k']}: peaks={np.round(row['r_peaks'],1)} delta={row['delta']:.1f} Delta={row['Delta']}\n")
                    f.write(f"  Result Ratio: {d_item['res']['ratio']}\n")
        print(f"Saved: {fname}")

    def on_click(self, event):
        if event.inaxes == self.ax_img:
            self.data[self.idx]['center'] = (int(event.xdata), int(event.ydata))
            self.process_frame(self.idx); self.update_view()
    def change_mode(self, label):
        self.mode = 'triplet' if 'Триплет' in label else 'doublet'
        self.recalc_all(); self.update_view()
    def next_img(self, event):
        self.idx = (self.idx + 1) % len(self.data); self.update_view()
    def prev_img(self, event):
        self.idx = (self.idx - 1) % len(self.data); self.update_view()

# =========================================================================
# 4. ЗАПУСК
# =========================================================================
if __name__ == "__main__":
    # --- СПИСОК ВАШИХ ФАЙЛОВ ---
    
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