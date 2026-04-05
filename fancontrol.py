#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk
import subprocess
import threading
import time

BG = "#0e0e0e"
CARD = "#161616"
ACCENT = "#00e5ff"
ACCENT2 = "#ff4081"
TEXT = "#f0f0f0"
MUTED = "#555"
GREEN = "#00e676"

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

class FanControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fan Control")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        self.cpu_speed = tk.IntVar(value=50)
        self.gpu_speed = tk.IntVar(value=50)
        self.build_ui()
        self.start_polling()

    def make_fan_section(self, parent, label, speed_var, on_auto, on_apply, accent):
        frame = tk.Frame(parent, bg=CARD, padx=16, pady=12)
        frame.pack(fill="x", padx=16, pady=6)

        header = tk.Frame(frame, bg=CARD)
        header.pack(fill="x")
        tk.Label(header, text=label, bg=CARD, fg=MUTED,
                 font=("Courier New", 8)).pack(side="left")
        status_lbl = tk.Label(header, text="● AUTO", bg=CARD, fg=GREEN,
                              font=("Courier New", 8, "bold"))
        status_lbl.pack(side="right")

        btn_row = tk.Frame(frame, bg=CARD)
        btn_row.pack(fill="x", pady=8)

        btn_auto = tk.Button(btn_row, text="AUTO", bg=GREEN, fg="#000",
                             font=("Courier New", 9, "bold"), relief="flat",
                             width=8, cursor="hand2")
        btn_auto.pack(side="left", padx=(0, 8))

        btn_manual = tk.Button(btn_row, text="MANUAL", bg=CARD, fg=MUTED,
                               font=("Courier New", 9, "bold"), relief="flat",
                               width=8, cursor="hand2",
                               highlightbackground=MUTED, highlightthickness=1)
        btn_manual.pack(side="left")

        speed_frame = tk.Frame(frame, bg=CARD)

        tk.Label(speed_frame, text="SPEED", bg=CARD, fg=MUTED,
                 font=("Courier New", 8)).pack(anchor="w")

        slider_row = tk.Frame(speed_frame, bg=CARD)
        slider_row.pack(fill="x")

        speed_val_lbl = tk.Label(slider_row, text="50%", bg=CARD, fg=accent,
                                 font=("Courier New", 11, "bold"), width=5)

        slider = ttk.Scale(slider_row, from_=0, to=100, variable=speed_var,
                           orient="horizontal", length=200,
                           command=lambda v: speed_val_lbl.config(text=f"{int(float(v))}%"))
        slider.pack(side="left", padx=(0, 8))
        speed_val_lbl.pack(side="left")

        apply_btn = tk.Button(speed_frame, text="APPLY", bg=accent, fg="#000",
                              font=("Courier New", 9, "bold"), relief="flat",
                              cursor="hand2", pady=4)
        apply_btn.pack(fill="x", pady=(8, 0))

        def _auto():
            on_auto()
            speed_frame.pack_forget()
            btn_auto.config(bg=GREEN, fg="#000")
            btn_manual.config(bg=CARD, fg=MUTED)
            status_lbl.config(text="● AUTO", fg=GREEN)

        def _manual():
            speed_frame.pack(fill="x", pady=(4, 0))
            btn_manual.config(bg=accent, fg="#000")
            btn_auto.config(bg=CARD, fg=MUTED)
            status_lbl.config(text="● MANUAL", fg=accent)

        def _apply():
            on_apply(speed_var.get())
            apply_btn.config(text="✓ APPLIED", bg=GREEN)
            self.root.after(1500, lambda: apply_btn.config(text="APPLY", bg=accent))

        btn_auto.config(command=_auto)
        btn_manual.config(command=_manual)
        apply_btn.config(command=_apply)

    def build_ui(self):
        tk.Label(self.root, text="⚙ FAN CONTROL", bg=BG, fg=ACCENT,
                 font=("Courier New", 14, "bold")).pack(pady=(18, 4))
        tk.Frame(self.root, bg=MUTED, height=1, width=320).pack(pady=4)

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

        self.make_fan_section(
            self.root, "CPU FAN", self.cpu_speed,
            on_auto=lambda: run("sudo nbfc set -a"),
            on_apply=lambda s: run(f"sudo nbfc set -s {s}"),
            accent=ACCENT
        )

        self.make_fan_section(
            self.root, "GPU FAN", self.gpu_speed,
            on_auto=lambda: run("nvidia-settings -a '[gpu:0]/GPUFanControlState=0'"),
            on_apply=lambda s: (
                run("nvidia-settings -a '[gpu:0]/GPUFanControlState=1'"),
                run(f"nvidia-settings -a '[fan:0]/GPUTargetFanSpeed={s}'")
            ),
            accent=ACCENT2
        )

        tk.Label(self.root, text="nbfc + nvidia-settings  |  OMEN 16",
                 bg=BG, fg=MUTED, font=("Courier New", 8)).pack(pady=(4, 14))

    def poll_temps(self):
        while True:
            cpu_t = get_temp("/sys/class/hwmon/hwmon6/temp1_input")
            if cpu_t is None:
                for i in range(10):
                    t = get_temp(f"/sys/class/hwmon/hwmon{i}/temp1_input")
                    if t and 20 < t < 120:
                        cpu_t = t
                        break

            gpu_t = get_temp("/sys/class/hwmon/hwmon5/temp1_input")
            if gpu_t is None:
                out, _ = run("nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader")
                try:
                    gpu_t = float(out)
                except:
                    gpu_t = None

            def update(c=cpu_t, g=gpu_t):
                if c:
                    col = ACCENT2 if c > 80 else (ACCENT if c > 60 else GREEN)
                    self.cpu_temp_lbl.config(text=f"CPU  {c}°C", fg=col)
                if g:
                    col = ACCENT2 if g > 80 else (ACCENT if g > 60 else GREEN)
                    self.gpu_temp_lbl.config(text=f"GPU  {g}°C", fg=col)

            self.root.after(0, update)
            time.sleep(2)

    def start_polling(self):
        threading.Thread(target=self.poll_temps, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("360x560")
    app = FanControlApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (root.destroy(), exit(0)))
    root.mainloop()
