#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk
import subprocess
import threading
import time
import json
import os

try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False

BG      = "#0e0e0e"
CARD    = "#161616"
ACCENT  = "#00e5ff"
ACCENT2 = "#ff4081"
TEXT    = "#f0f0f0"
MUTED   = "#555"
GREEN   = "#00e676"
YELLOW  = "#ffea00"
GRID    = "#222222"

CONFIG_FILE = os.path.expanduser("~/.config/fancontrol.json")

DEFAULT_CURVE = [[30, 0], [50, 20], [60, 40], [70, 65], [80, 85], [90, 100]]

PRESETS = {
    "Silent":      {"speed": 30,  "color": GREEN,   "auto": False},
    "Balanced":    {"speed": 60,  "color": YELLOW,  "auto": False},
    "Performance": {"speed": 100, "color": ACCENT2, "auto": False},
    "Auto":        {"speed": 0,   "color": ACCENT,  "auto": True},
}

def run(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return r.stdout.strip(), r.returncode
    except Exception as e:
        return str(e), 1

def get_temp(path):
    try:
        with open(path) as f:
            return round(int(f.read().strip()) / 1000, 1)
    except:
        return None

def get_cpu_temp():
    t = get_temp("/sys/class/hwmon/hwmon6/temp1_input")
    if t: return t
    for i in range(10):
        t = get_temp(f"/sys/class/hwmon/hwmon{i}/temp1_input")
        if t and 20 < t < 120:
            return t
    return None

def get_gpu_temp():
    t = get_temp("/sys/class/hwmon/hwmon5/temp1_input")
    if t: return t
    out, _ = run("nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader")
    try: return float(out)
    except: return None

def curve_speed(temp, curve):
    pts = sorted(curve)
    if temp <= pts[0][0]:  return pts[0][1]
    if temp >= pts[-1][0]: return pts[-1][1]
    for i in range(len(pts) - 1):
        t0, s0 = pts[i]; t1, s1 = pts[i+1]
        if t0 <= temp <= t1:
            return int(s0 + (s1 - s0) * (temp - t0) / (t1 - t0))
    return 100

def save_config(data):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

def load_config():
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except:
        return {"preset": "Auto", "speed": 50, "curve": DEFAULT_CURVE}

# ── Curve Editor ─────────────────────────────────────────────────────────────

class CurveEditor(tk.Toplevel):
    W, H = 320, 220
    PAD = 30

    def __init__(self, parent, curve, on_save):
        super().__init__(parent)
        self.title("Edit Fan Curve")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.on_save = on_save
        self.curve = [list(p) for p in curve]
        self.drag_idx = None

        tk.Label(self, text="EDIT AUTO CURVE", bg=BG, fg=ACCENT,
                 font=("Courier New", 11, "bold")).pack(pady=(14, 4))
        tk.Label(self, text="Drag points  •  X = Temperature  •  Y = Fan Speed %",
                 bg=BG, fg=MUTED, font=("Courier New", 7)).pack()

        self.canvas = tk.Canvas(self, width=self.W, height=self.H,
                                bg=CARD, highlightthickness=0)
        self.canvas.pack(padx=16, pady=10)

        self.canvas.bind("<ButtonPress-1>",   self.on_press)
        self.canvas.bind("<B1-Motion>",       self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Button-3>",        self.on_right_click)

        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(pady=(0, 14))
        tk.Button(btn_row, text="Reset", bg=CARD, fg=MUTED,
                  font=("Courier New", 9), relief="flat", cursor="hand2",
                  command=self.reset).pack(side="left", padx=(0, 8))
        tk.Button(btn_row, text="Save & Apply", bg=ACCENT, fg="#000",
                  font=("Courier New", 9, "bold"), relief="flat", cursor="hand2",
                  command=self.save).pack(side="left")

        tk.Label(self, text="Right-click canvas to add a point",
                 bg=BG, fg=MUTED, font=("Courier New", 7)).pack(pady=(0, 8))

        self.draw()

    def temp_to_x(self, t): return self.PAD + (t - 20) / 80 * (self.W - 2*self.PAD)
    def speed_to_y(self, s): return self.H - self.PAD - s / 100 * (self.H - 2*self.PAD)
    def x_to_temp(self, x):  return max(20, min(100, 20 + (x - self.PAD) / (self.W - 2*self.PAD) * 80))
    def y_to_speed(self, y): return max(0,  min(100, (1 - (y - self.PAD) / (self.H - 2*self.PAD)) * 100))

    def draw(self):
        c = self.canvas
        c.delete("all")
        p = self.PAD
        w, h = self.W, self.H

        # Grid
        for t in range(20, 101, 10):
            x = self.temp_to_x(t)
            c.create_line(x, p, x, h-p, fill=GRID)
            c.create_text(x, h-p+10, text=str(t), fill=MUTED, font=("Courier New", 6))
        for s in range(0, 101, 20):
            y = self.speed_to_y(s)
            c.create_line(p, y, w-p, y, fill=GRID)
            c.create_text(p-10, y, text=str(s), fill=MUTED, font=("Courier New", 6))

        # Axis labels
        c.create_text(w//2, h-4, text="Temp (°C)", fill=MUTED, font=("Courier New", 7))
        c.create_text(8, h//2, text="Speed %", fill=MUTED, font=("Courier New", 7), angle=90)

        pts = sorted(self.curve)

        # Line
        for i in range(len(pts)-1):
            x0 = self.temp_to_x(pts[i][0]); y0 = self.speed_to_y(pts[i][1])
            x1 = self.temp_to_x(pts[i+1][0]); y1 = self.speed_to_y(pts[i+1][1])
            c.create_line(x0, y0, x1, y1, fill=ACCENT, width=2)

        # Points
        for i, (t, s) in enumerate(pts):
            x = self.temp_to_x(t); y = self.speed_to_y(s)
            c.create_oval(x-6, y-6, x+6, y+6, fill=ACCENT, outline=BG, width=2, tags=f"pt{i}")
            c.create_text(x, y-14, text=f"{int(t)}°/{int(s)}%",
                          fill=TEXT, font=("Courier New", 6))

    def find_point(self, x, y, thresh=12):
        pts = sorted(self.curve)
        for i, (t, s) in enumerate(pts):
            px = self.temp_to_x(t); py = self.speed_to_y(s)
            if abs(px - x) < thresh and abs(py - y) < thresh:
                return i
        return None

    def on_press(self, e):
        self.drag_idx = self.find_point(e.x, e.y)

    def on_drag(self, e):
        if self.drag_idx is None: return
        pts = sorted(self.curve)
        t = round(self.x_to_temp(e.x))
        s = round(self.y_to_speed(e.y))
        pts[self.drag_idx] = [t, s]
        self.curve = pts
        self.draw()

    def on_release(self, e):
        self.drag_idx = None

    def on_right_click(self, e):
        t = round(self.x_to_temp(e.x))
        s = round(self.y_to_speed(e.y))
        self.curve.append([t, s])
        self.draw()

    def reset(self):
        self.curve = [list(p) for p in DEFAULT_CURVE]
        self.draw()

    def save(self):
        self.on_save(sorted(self.curve))
        self.destroy()


# ── Main App ─────────────────────────────────────────────────────────────────

class FanControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fan Control")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        self.cpu_speed  = tk.IntVar(value=50)
        self.auto_curve = True
        cfg = load_config()
        self.curve = cfg.get("curve", DEFAULT_CURVE)
        self.build_ui()
        self.apply_preset(cfg.get("preset", "Auto"), save=False)
        self.start_polling()
        if TRAY_AVAILABLE:
            self.setup_tray()

    def build_ui(self):
        title_row = tk.Frame(self.root, bg=BG)
        title_row.pack(fill="x", padx=16, pady=(16, 4))
        tk.Label(title_row, text="⚙ FAN CONTROL", bg=BG, fg=ACCENT,
                 font=("Courier New", 14, "bold")).pack(side="left")
        if TRAY_AVAILABLE:
            tk.Button(title_row, text="⎙", bg=BG, fg=MUTED, relief="flat",
                      font=("Courier New", 12), cursor="hand2",
                      command=self.hide_to_tray).pack(side="right")
        tk.Frame(self.root, bg=MUTED, height=1).pack(fill="x", padx=16, pady=4)

        # Temps
        tf = tk.Frame(self.root, bg=CARD, padx=16, pady=12)
        tf.pack(fill="x", padx=16, pady=6)
        tk.Label(tf, text="TEMPERATURES", bg=CARD, fg=MUTED,
                 font=("Courier New", 8)).pack(anchor="w")
        row = tk.Frame(tf, bg=CARD)
        row.pack(fill="x", pady=4)
        self.cpu_temp_lbl = tk.Label(row, text="CPU  —", bg=CARD, fg=TEXT,
                                     font=("Courier New", 11, "bold"), width=14, anchor="w")
        self.cpu_temp_lbl.pack(side="left")
        self.gpu_temp_lbl = tk.Label(row, text="GPU  —", bg=CARD, fg=TEXT,
                                     font=("Courier New", 11, "bold"), width=14, anchor="w")
        self.gpu_temp_lbl.pack(side="left")

        # Presets
        pf = tk.Frame(self.root, bg=CARD, padx=16, pady=12)
        pf.pack(fill="x", padx=16, pady=6)
        tk.Label(pf, text="PRESET", bg=CARD, fg=MUTED,
                 font=("Courier New", 8)).pack(anchor="w", pady=(0, 6))
        br = tk.Frame(pf, bg=CARD)
        br.pack(fill="x")
        self.preset_btns = {}
        for name, data in PRESETS.items():
            b = tk.Button(br, text=name, bg=CARD, fg=MUTED,
                          font=("Courier New", 8, "bold"), relief="flat",
                          cursor="hand2", padx=6, pady=4,
                          command=lambda n=name: self.apply_preset(n))
            b.pack(side="left", padx=(0, 6))
            self.preset_btns[name] = b

        # Manual speed
        mf = tk.Frame(self.root, bg=CARD, padx=16, pady=12)
        mf.pack(fill="x", padx=16, pady=6)
        hdr = tk.Frame(mf, bg=CARD)
        hdr.pack(fill="x")
        tk.Label(hdr, text="MANUAL SPEED", bg=CARD, fg=MUTED,
                 font=("Courier New", 8)).pack(side="left")
        self.status_lbl = tk.Label(hdr, text="● AUTO CURVE", bg=CARD, fg=GREEN,
                                   font=("Courier New", 8, "bold"))
        self.status_lbl.pack(side="right")

        sr = tk.Frame(mf, bg=CARD)
        sr.pack(fill="x", pady=(8, 0))
        self.speed_val_lbl = tk.Label(sr, text="—%", bg=CARD, fg=ACCENT,
                                      font=("Courier New", 11, "bold"), width=5)
        style = ttk.Style(); style.theme_use("clam")
        style.configure("C.Horizontal.TScale", background=CARD, troughcolor="#222",
                        sliderthickness=14, sliderrelief="flat")
        self.slider = ttk.Scale(sr, from_=0, to=100, variable=self.cpu_speed,
                                orient="horizontal", style="C.Horizontal.TScale", length=190,
                                command=lambda v: self.speed_val_lbl.config(text=f"{int(float(v))}%"))
        self.slider.pack(side="left", padx=(0, 8))
        self.speed_val_lbl.pack(side="left")

        btn_row = tk.Frame(mf, bg=CARD)
        btn_row.pack(fill="x", pady=(10, 0))
        self.apply_btn = tk.Button(btn_row, text="APPLY MANUAL",
                                   command=self.apply_manual,
                                   bg=ACCENT, fg="#000", font=("Courier New", 9, "bold"),
                                   relief="flat", cursor="hand2", pady=4)
        self.apply_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))
        tk.Button(btn_row, text="✎ CURVE", command=self.open_curve_editor,
                  bg=CARD, fg=ACCENT, font=("Courier New", 9, "bold"),
                  relief="flat", cursor="hand2", pady=4,
                  highlightbackground=ACCENT, highlightthickness=1).pack(side="left")

        tk.Label(self.root, text="nbfc-linux  |  HP OMEN 16",
                 bg=BG, fg=MUTED, font=("Courier New", 8)).pack(pady=(4, 14))

    def open_curve_editor(self):
        CurveEditor(self.root, self.curve, self.on_curve_saved)

    def on_curve_saved(self, new_curve):
        self.curve = new_curve
        cfg = load_config()
        cfg["curve"] = new_curve
        save_config(cfg)

    def apply_preset(self, name, save=True):
        if name not in PRESETS:
            name = "Auto"
        data = PRESETS[name]
        for n, btn in self.preset_btns.items():
            btn.config(bg=data["color"] if n == name else CARD,
                       fg="#000" if n == name else MUTED)
        if data["auto"]:
            self.auto_curve = True
            self.status_lbl.config(text="● AUTO CURVE", fg=GREEN)
            self.speed_val_lbl.config(text="—%")
        else:
            self.auto_curve = False
            run(f"sudo nbfc set -s {data['speed']}")
            self.status_lbl.config(text=f"● {name.upper()}", fg=data["color"])
            self.speed_val_lbl.config(text=f"{data['speed']}%")
            self.cpu_speed.set(data["speed"])
        if save:
            cfg = load_config(); cfg["preset"] = name; save_config(cfg)

    def apply_manual(self):
        speed = self.cpu_speed.get()
        self.auto_curve = False
        run(f"sudo nbfc set -s {speed}")
        for b in self.preset_btns.values(): b.config(bg=CARD, fg=MUTED)
        self.status_lbl.config(text=f"● MANUAL {speed}%", fg=ACCENT)
        self.apply_btn.config(text="✓ APPLIED", bg=GREEN)
        self.root.after(1500, lambda: self.apply_btn.config(text="APPLY MANUAL", bg=ACCENT))
        save_config({"preset": "Manual", "speed": speed, "curve": self.curve})

    def poll_temps(self):
        while True:
            cpu_t = get_cpu_temp()
            gpu_t = get_gpu_temp()
            if self.auto_curve and cpu_t:
                spd = curve_speed(cpu_t, self.curve)
                run(f"sudo nbfc set -s {spd}")
            def update(c=cpu_t, g=gpu_t):
                if c:
                    col = ACCENT2 if c > 80 else (YELLOW if c > 65 else GREEN)
                    self.cpu_temp_lbl.config(text=f"CPU  {c}°C", fg=col)
                    if self.auto_curve:
                        self.speed_val_lbl.config(text=f"{curve_speed(c, self.curve)}%")
                if g:
                    col = ACCENT2 if g > 80 else (YELLOW if g > 65 else GREEN)
                    self.gpu_temp_lbl.config(text=f"GPU  {g}°C", fg=col)
            self.root.after(0, update)
            time.sleep(3)

    def start_polling(self):
        threading.Thread(target=self.poll_temps, daemon=True).start()

    def make_tray_icon(self):
        img = Image.new("RGB", (64, 64), (14, 14, 14))
        d = ImageDraw.Draw(img)
        d.ellipse([8, 8, 56, 56], fill=(0, 229, 255))
        d.ellipse([20, 20, 44, 44], fill=(14, 14, 14))
        return img

    def setup_tray(self):
        menu = pystray.Menu(
            pystray.MenuItem("Show", self.show_window, default=True),
            pystray.MenuItem("Silent",      lambda: self.root.after(0, lambda: self.apply_preset("Silent"))),
            pystray.MenuItem("Balanced",    lambda: self.root.after(0, lambda: self.apply_preset("Balanced"))),
            pystray.MenuItem("Performance", lambda: self.root.after(0, lambda: self.apply_preset("Performance"))),
            pystray.MenuItem("Auto",        lambda: self.root.after(0, lambda: self.apply_preset("Auto"))),
            pystray.MenuItem("Quit",        self.quit_app),
        )
        self.tray = pystray.Icon("fancontrol", self.make_tray_icon(), "Fan Control", menu)
        threading.Thread(target=self.tray.run, daemon=True).start()

    def hide_to_tray(self):
        self.root.withdraw()

    def show_window(self):
        self.root.after(0, self.root.deiconify)

    def quit_app(self):
        if TRAY_AVAILABLE: self.tray.stop()
        self.root.after(0, lambda: (self.root.destroy(), exit(0)))


if __name__ == "__main__":
    if not TRAY_AVAILABLE:
        print("Tip: pip install pystray pillow --break-system-packages")
    root = tk.Tk()
    root.geometry("360x530")
    app = FanControlApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (
        app.hide_to_tray() if TRAY_AVAILABLE else (root.destroy(), exit(0))
    ))
    root.mainloop()
