# HP OMEN CPU Fan Control for Linux

A lightweight GUI app for controlling the **CPU fan** on HP OMEN laptops running Linux.

Built with **nbfc-linux** for fan control and **Python Tkinter** for the graphical interface.

![Python](https://img.shields.io/badge/Python-3.x-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Linux-orange)

---

## ✨ Features

* 🌡 Live CPU and GPU temperature monitoring
* 🎚 Fan presets:

  * Silent
  * Balanced
  * Performance
  * Auto Curve
* 📈 Custom fan curve editor
* 🎛 Manual fan speed slider
* 💾 Settings saved across reboots
* 🖥 Optional system tray support
* 🌙 Clean dark-themed UI
* 🔁 Restores native auto mode when app closes

---

## 🧪 Tested On

* **Laptop:** HP OMEN 16 (16-xd0xxx)
* **CPU:** AMD Ryzen 7 7840HS
* **GPU:** NVIDIA RTX 4050 Laptop
* **OS:** Fedora 43 XFCE

Should work on other HP OMEN models, but compatibility may vary.

---

## 📸 Screenshots

### Main Window

<img width="361" height="553" alt="Main UI" src="https://github.com/user-attachments/assets/f97380e8-a725-4836-90ad-3521b1f4d0a0" />

### Curve Editor

<img width="357" height="381" alt="Curve Editor" src="https://github.com/user-attachments/assets/c91abd30-702b-45cd-82f7-58f323152c48" />

---

## ⬇ Download

[Download ZIP](https://github.com/ADITYA-TUMMURI/Hp-OMEN-cpu-fan-control/archive/refs/heads/main.zip)

Or clone:

```bash
git clone https://github.com/ADITYA-TUMMURI/Hp-OMEN-cpu-fan-control.git
cd Hp-OMEN-cpu-fan-control
```

---

## ⚡ Quick Install (Recommended)

```bash
git clone https://github.com/ADITYA-TUMMURI/Hp-OMEN-cpu-fan-control.git
cd Hp-OMEN-cpu-fan-control
chmod +x install.sh
./install.sh
```

---

## 🛠 Manual Installation

### 1. Install Dependencies

```bash
sudo dnf install -y git cmake autoconf automake libtool libcurl-devel \
openssl-devel python3-tkinter acpica-tools dkms kernel-devel
```

### 2. Build NBFC

```bash
git clone https://github.com/nbfc-linux/nbfc-linux.git
cd nbfc-linux
./autogen.sh
./configure
make -j$(nproc)
sudo make install
cd ~
```

### 3. Install acpi_call

```bash
git clone https://github.com/nix-community/acpi_call.git
cd acpi_call
sudo make
sudo make install
sudo modprobe acpi_call
cd ~
```

### 4. Configure Fan Control

```bash
sudo nbfc rate-config -a
sudo nbfc config --apply "HP 15 Notebook PC"
sudo systemctl enable --now nbfc_service
```

### 5. Run App

```bash
/usr/bin/python3 fancontrol.py
```

Or search in app menu:

**Fan Control**

---

## 🧠 Auto Modes Explained

### Native Auto Mode

Uses laptop firmware / NBFC automatic control.

### Auto Curve Mode

Uses the app’s custom temperature curve while the app is open or minimized.

When the app exits, native auto mode is restored automatically.

---

## 📋 Usage

| Action        | Result            |
| ------------- | ----------------- |
| Silent        | Lowest noise      |
| Balanced      | Daily use         |
| Performance   | Maximum cooling   |
| Auto          | Dynamic fan curve |
| Manual Slider | Fixed fan speed   |

---

## ⚠ Notes

* Currently designed for **CPU fan control**
* On many HP OMEN laptops, **GPU fan remains firmware-controlled**
* Always monitor temperatures after custom fan settings

---

## 🔧 Troubleshooting

### App does not launch

```bash
/usr/bin/python3 fancontrol.py
```

### tkinter error

```bash
sudo dnf install python3-tkinter
```

### NBFC socket error

```bash
sudo systemctl enable --now nbfc_service
```

### Check current status

```bash
sudo nbfc status
```

---

## 🚀 Roadmap

* Better distro support
* Notifications
* Dual-fan support (if EC allows)
* RPM package
* Improved tray support

---

## 🤝 Contributing

Pull requests and compatibility reports are welcome.

---

## 📄 License

MIT
