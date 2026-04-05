# HP OMEN CPU Fan Control for Linux

A lightweight GUI app to control the CPU fan on HP OMEN laptops running Linux.

Built with `nbfc-linux` for fan control and Python `tkinter` for the interface.

![Python](https://img.shields.io/badge/Python-3.x-blue) ![License](https://img.shields.io/badge/License-MIT-green) ![Platform](https://img.shields.io/badge/Platform-Linux-orange)

---

## Tested On

- **Laptop:** HP OMEN 16 (16-xd0xxx)
- **CPU:** AMD Ryzen 7 7840HS
- **GPU:** NVIDIA RTX 4050 Laptop
- **OS:** Fedora 43 XFCE

Should work on other HP OMEN models — your mileage may vary.

---

## Features

- Live CPU and GPU temperature display (color coded)
- **Presets** — Silent, Balanced, Performance, Auto
- **Auto curve** — automatically adjusts fan speed based on CPU temperature
- **Curve editor** — drag points on a graph to set your own temp→speed curve
- Manual fan speed slider (0–100%)
- Settings saved across reboots
- System tray support (optional)
- Clean dark-themed GUI — no terminal needed after setup

---
<img width="361" height="553" alt="image" src="https://github.com/user-attachments/assets/f97380e8-a725-4836-90ad-3521b1f4d0a0" />


<img width="357" height="381" alt="image" src="https://github.com/user-attachments/assets/c91abd30-702b-45cd-82f7-58f323152c48" />


## Download

**[⬇ Download the latest version](https://github.com/ADITYA-TUMMURI/Hp-OMEN-cpu-fan-control/archive/refs/heads/main.zip)**

Or clone with git:

```bash
git clone https://github.com/ADITYA-TUMMURI/Hp-OMEN-cpu-fan-control.git
cd Hp-OMEN-cpu-fan-control
```

---

## Installation

### Quick Install (recommended)

```bash
git clone https://github.com/ADITYA-TUMMURI/Hp-OMEN-cpu-fan-control.git
cd Hp-OMEN-cpu-fan-control
chmod +x install.sh
./install.sh
```

That's it. The script handles everything automatically.

---

### Manual Install

**1. Install dependencies**

```bash
sudo dnf install -y git cmake autoconf automake libtool libcurl-devel \
    openssl-devel python3-tkinter acpica-tools dkms kernel-devel
```

**2. Build nbfc-linux**

```bash
git clone https://github.com/nbfc-linux/nbfc-linux.git
cd nbfc-linux && ./autogen.sh && ./configure
make -j$(nproc) && sudo make install
cd ~
```

**3. Install acpi_call module**

```bash
git clone https://github.com/nix-community/acpi_call.git
cd acpi_call && sudo make && sudo make install
sudo modprobe acpi_call
cd ~
```

**4. Configure nbfc for your laptop**

```bash
sudo nbfc rate-config -a
sudo nbfc config --apply "HP 15 Notebook PC"
sudo nbfc start
```

**5. Auto-start nbfc on boot**

```bash
echo 'sudo nbfc start' | sudo tee /etc/rc.d/rc.local
sudo chmod +x /etc/rc.d/rc.local
```

**6. Set up the app**

```bash
mkdir -p ~/.local/share/icons
cp fancontrol.svg ~/.local/share/icons/fancontrol.svg
cp fancontrol.desktop ~/.local/share/applications/
cp fancontrol.py ~/fancontrol.py
```

**7. Allow passwordless sudo for nbfc**

```bash
sudo visudo -f /etc/sudoers.d/fancontrol
```

Add (replace `yourusername`):
```
yourusername ALL=(ALL) NOPASSWD: ALL
```

**8. Run the app**

```bash
sudo python3 ~/fancontrol.py
```

Or search **Fan Control** in your app menu.

---

## Optional — System Tray Support

```bash
pip install pystray pillow --break-system-packages
```

Once installed, closing the window minimizes to tray instead of quitting.

---

## Usage

| Action | How |
|---|---|
| Quick presets | Click Silent / Balanced / Performance / Auto |
| Auto fan curve | Click **Auto** — fan adjusts based on temperature automatically |
| Edit curve | Click **✎ CURVE** — drag points on the graph |
| Manual speed | Adjust slider → click **Apply Manual** |

---

## Notes

- **GPU fan** is locked by NVIDIA on all laptop GPUs — cannot be controlled on Linux
- Install script uses `dnf` (Fedora/RHEL). On Ubuntu/Debian replace `dnf` with `apt`, on Arch use `pacman`

---

## License

MIT
