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

BG = "#0e0e0e"
CARD = "#161616"
ACCENT = "#00e5ff"
ACCENT2 = "#ff4081"
TEXT = "#f0f0f0"
MUTED = "#555"
GREEN = "#00e676"
YELLOW = "#ffea00"

CONFIG_FILE = os.path.expanduser("~/.config/fancontrol.json")

PRESETS = {
    "Silent":      {"speed": 30,  "color": GREEN,   "auto_curve": False},
    "Balanced":    {"speed": 60,  "color": YELLOW,  "auto_curve": False},
    "Performance": {"speed": 100, "color": ACCENT2, "auto_curve": False},
    "Auto":        {"speed": 0,   "color": ACCENT,  "auto_curve": True},
}

AUTO_CURVE = [
    (0,  40,  0),
    (40, 55,  30),
    (55, 65,  50),
    (65, 75,  70),
    (75, 85,  85),
    (85, 200, 100),
]

def run(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.returncode
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

def curve_speed(temp):
    for lo, hi, spd in AUTO_CURVE:
        if lo <= temp < hi:
            return spd
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
        return {"preset": "Auto", "speed": 50}

class FanControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fan Control")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        self.cpu_speed = tk.IntVar(value=50)
        self.current_preset = tk.StringVar(value="Auto")
        self.auto_curve_active = True
        self.hidden = False
        cfg = load_config()
        self.current_preset.set(cfg.get("preset", "Auto"))
        self.cpu_speed.set(cfg.get("speed", 50))
        self.build_ui()
        self.apply_preset(self.current_preset.get(), save=False)
        self.start_polling()
        if TRAY_AVAILABLE:
            self.setup_tray()

    def build_ui(self):
        # Title
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
        temp_frame = tk.Frame(self.root, bg=CARD, padx=16, pady=12)
        temp_frame.pack(fill="x", padx=16, pady=6)
        tk.Label(temp_frame, text="TEMPERATURES", bg=CARD, fg=MUTED,
                 font=("Courier New", 8)).pack(anchor="w")
        row = tk.Frame(temp_frame, bg=CARD)
        row.pack(fill="x", pady=4)
        self.cpu_temp_lbl = tk.Label(row, text="CPU  —", bg=CARD, fg=TEXT,
                                     font=("Courier New", 11, "bold"), width=14, anchor="w")
        self.cpu_temp_lbl.pack(side="left")
        self.gpu_temp_lbl = tk.Label(row, text="GPU  —", bg=CARD, fg=TEXT,
                                     font=("Courier New", 11, "bold"), width=14, anchor="w")
        self.gpu_temp_lbl.pack(side="left")

        # Presets
        preset_frame = tk.Frame(self.root, bg=CARD, padx=16, pady=12)
        preset_frame.pack(fill="x", padx=16, pady=6)
        tk.Label(preset_frame, text="PRESET", bg=CARD, fg=MUTED,
                 font=("Courier New", 8)).pack(anchor="w", pady=(0, 6))
        btn_row = tk.Frame(preset_frame, bg=CARD)
        btn_row.pack(fill="x")
        self.preset_btns = {}
        for name, data in PRESETS.items():
            btn = tk.Button(btn_row, text=name, bg=CARD, fg=MUTED,
                            font=("Courier New", 8, "bold"), relief="flat",
                            cursor="hand2", padx=6, pady=4,
                            command=lambda n=name: self.apply_preset(n))
            btn.pack(side="left", padx=(0, 6))
            self.preset_btns[name] = btn

        # Manual
        manual_frame = tk.Frame(self.root, bg=CARD, padx=16, pady=12)
        manual_frame.pack(fill="x", padx=16, pady=6)
        header = tk.Frame(manual_frame, bg=CARD)
        header.pack(fill="x")
        tk.Label(header, text="MANUAL SPEED", bg=CARD, fg=MUTED,
                 font=("Courier New", 8)).pack(side="left")
        self.status_lbl = tk.Label(header, text="● AUTO CURVE", bg=CARD, fg=GREEN,
                                   font=("Courier New", 8, "bold"))
        self.status_lbl.pack(side="right")

        slider_row = tk.Frame(manual_frame, bg=CARD)
        slider_row.pack(fill="x", pady=(8, 0))

        self.speed_val_lbl = tk.Label(slider_row, text="—%", bg=CARD, fg=ACCENT,
                                      font=("Courier New", 11, "bold"), width=5)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("C.Horizontal.TScale", background=CARD, troughcolor="#222",
                        sliderthickness=14, sliderrelief="flat")

        self.slider = ttk.Scale(slider_row, from_=0, to=100, variable=self.cpu_speed,
                                orient="horizontal", style="C.Horizontal.TScale", length=190,
                                command=lambda v: self.speed_val_lbl.config(text=f"{int(float(v))}%"))
        self.slider.pack(side="left", padx=(0, 8))
        self.speed_val_lbl.pack(side="left")

        self.apply_btn = tk.Button(manual_frame, text="APPLY MANUAL",
                                   command=self.apply_manual,
                                   bg=ACCENT, fg="#000", font=("Courier New", 9, "bold"),
                                   relief="flat", cursor="hand2", pady=4)
        self.apply_btn.pack(fill="x", pady=(10, 0))

        # Auto curve info
        self.curve_lbl = tk.Label(self.root,
                                  text="Auto curve: 30%@55° · 50%@65° · 70%@75° · 100%@85°",
                                  bg=BG, fg=MUTED, font=("Courier New", 7))
        self.curve_lbl.pack(pady=(0, 4))

        tk.Label(self.root, text="nbfc-linux  |  HP OMEN 16",
                 bg=BG, fg=MUTED, font=("Courier New", 8)).pack(pady=(0, 14))

    def apply_preset(self, name, save=True):
        self.current_preset.set(name)
        data = PRESETS[name]
        for n, btn in self.preset_btns.items():
            if n == name:
                btn.config(bg=data["color"], fg="#000")
            else:
                btn.config(bg=CARD, fg=MUTED)

        if data["auto_curve"]:
            self.auto_curve_active = True
            run("sudo nbfc set -a")
            self.status_lbl.config(text="● AUTO CURVE", fg=GREEN)
            self.speed_val_lbl.config(text="—%")
        else:
            self.auto_curve_active = False
            run(f"sudo nbfc set -s {data['speed']}")
            self.status_lbl.config(text=f"● {name.upper()}", fg=data["color"])
            self.speed_val_lbl.config(text=f"{data['speed']}%")
            self.cpu_speed.set(data["speed"])

        if save:
            save_config({"preset": name, "speed": data["speed"]})

    def apply_manual(self):
        speed = self.cpu_speed.get()
        self.auto_curve_active = False
        run(f"sudo nbfc set -s {speed}")
        for btn in self.preset_btns.values():
            btn.config(bg=CARD, fg=MUTED)
        self.status_lbl.config(text=f"● MANUAL {speed}%", fg=ACCENT)
        self.apply_btn.config(text="✓ APPLIED", bg=GREEN)
        self.root.after(1500, lambda: self.apply_btn.config(text="APPLY MANUAL", bg=ACCENT))
        save_config({"preset": "Manual", "speed": speed})

    def poll_temps(self):
        while True:
            cpu_t = get_cpu_temp()
            gpu_t = get_gpu_temp()

            if self.auto_curve_active and cpu_t:
                spd = curve_speed(cpu_t)
                run(f"sudo nbfc set -s {spd}")

            def update(c=cpu_t, g=gpu_t):
                if c:
                    col = ACCENT2 if c > 80 else (YELLOW if c > 65 else GREEN)
                    self.cpu_temp_lbl.config(text=f"CPU  {c}°C", fg=col)
                    if self.auto_curve_active:
                        spd = curve_speed(c)
                        self.speed_val_lbl.config(text=f"{spd}%")
                if g:
                    col = ACCENT2 if g > 80 else (YELLOW if g > 65 else GREEN)
                    self.gpu_temp_lbl.config(text=f"GPU  {g}°C", fg=col)

            self.root.after(0, update)
            time.sleep(3)

    def start_polling(self):
        threading.Thread(target=self.poll_temps, daemon=True).start()

    # ── Tray ──────────────────────────────────────────────
    def make_tray_icon(self):
        img = Image.new("RGB", (64, 64), color=(14, 14, 14))
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
        self.hidden = True

    def show_window(self):
        self.root.after(0, self.root.deiconify)
        self.hidden = False

    def quit_app(self):
        if TRAY_AVAILABLE:
            self.tray.stop()
        self.root.after(0, lambda: (self.root.destroy(), exit(0)))

if __name__ == "__main__":
    if not TRAY_AVAILABLE:
        print("Tip: install pystray and pillow for system tray support:")
        print("  pip install pystray pillow --break-system-packages")

    root = tk.Tk()
    root.geometry("360x580")
    app = FanControlApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (
        app.hide_to_tray() if TRAY_AVAILABLE else (root.destroy(), exit(0))
    ))
    root.mainloop()
