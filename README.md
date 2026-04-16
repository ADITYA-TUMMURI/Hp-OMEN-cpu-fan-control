# HP OMEN CPU Fan Control for Linux

A lightweight fan-control utility for **HP OMEN laptops on Linux** with a clean GUI, live temperatures, presets, and a custom automatic fan curve.

Built with **Python + Tkinter** for the interface and **nbfc-linux** for embedded controller fan control.

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Linux](https://img.shields.io/badge/Platform-Linux-orange)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

- 🌡 **Live CPU & GPU temperature monitoring**
- 🎚 **One-click presets**
  - Silent
  - Balanced
  - Performance
  - Auto Curve
- 📈 **Custom fan curve editor**
  - Drag points on graph
  - Temperature → Fan Speed mapping
- 🎛 **Manual fan speed control**
- 💾 Settings saved automatically
- 🖥 **System tray support**
- 🌙 Clean dark UI
- 🔁 Restores native auto mode when app exits

---

## 🧪 Tested On

| Component | Details |
|---|---|
| Laptop | HP OMEN 16 (16-xd0xxx) |
| CPU | AMD Ryzen 7 7840HS |
| GPU | NVIDIA RTX 4050 Laptop |
| OS | Fedora 43 XFCE |

Should work on other HP OMEN models, but results may vary.

---

## 📸 Screenshots

<img width="361" height="553" alt="Main UI" src="https://github.com/user-attachments/assets/f97380e8-a725-4836-90ad-3521b1f4d0a0" />

<img width="357" height="381" alt="Curve Editor" src="https://github.com/user-attachments/assets/c91abd30-702b-45cd-82f7-58f323152c48" />

---

## ⚡ Quick Install (Fedora)

```bash
git clone https://github.com/ADITYA-TUMMURI/Hp-OMEN-cpu-fan-control.git
cd Hp-OMEN-cpu-fan-control
chmod +x install.sh
./install.sh
🛠 Manual Installation
1. Install Dependencies
sudo dnf install -y git cmake autoconf automake libtool libcurl-devel \
openssl-devel python3-tkinter acpica-tools dkms kernel-devel
2. Build NBFC
git clone https://github.com/nbfc-linux/nbfc-linux.git
cd nbfc-linux
./autogen.sh
./configure
make -j$(nproc)
sudo make install
3. Start NBFC Service
sudo systemctl enable --now nbfc_service
4. Apply Recommended Config
sudo nbfc rate-config -a
sudo nbfc config --apply "HP 15 Notebook PC"
5. Run App
/usr/bin/python3 fancontrol.py
▶ Launch From Menu

If installed through script, search:

Fan Control

Or run manually:

/usr/bin/python3 ~/hp-omen-fan-control/fancontrol.py
🧠 How Auto Modes Work
Native Auto Mode

Uses laptop firmware / NBFC automatic control.

App Auto Curve

Uses your custom curve while app is open or minimized.

When the app closes, native auto mode is restored automatically.

📋 Usage
Action	Result
Silent	Low noise
Balanced	Daily use
Performance	Max cooling
Auto	Custom dynamic curve
Manual Slider	Fixed speed
⚠ Important Notes
This project currently controls the CPU fan on supported systems.
On many OMEN laptops, the GPU fan remains firmware-controlled.
Fan control support depends on EC compatibility.
Always monitor temperatures after applying custom settings.
🔧 Troubleshooting
App does not open

Use system Python:

/usr/bin/python3 fancontrol.py
tkinter error

Install:

sudo dnf install python3-tkinter
NBFC socket error

Start service:

sudo systemctl enable --now nbfc_service
Check status
sudo nbfc status
🚀 Roadmap
Dual-fan support (if EC allows)
Better distro installers
Notifications
RPM package
Wayland tray improvements
🤝 Contributing

Pull requests, fixes, and model compatibility reports are welcome.

📄 License

MIT License
