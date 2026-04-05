# HP OMEN CPU Fan Control for Linux

A simple GUI app to control the CPU fan on HP OMEN laptops running Linux.

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

- Live CPU and GPU temperature display
- CPU fan AUTO / MANUAL toggle
- Manual fan speed slider (0–100%)
- Clean dark-themed GUI
- No terminal needed after setup

---

## Installation

### 1. Install dependencies

```bash
sudo dnf install -y git cmake autoconf automake libtool libcurl-devel openssl-devel python3-tkinter acpica-tools
```

### 2. Build and install nbfc-linux

```bash
git clone https://github.com/nbfc-linux/nbfc-linux.git
cd nbfc-linux
./autogen.sh
./configure
make -j$(nproc)
sudo make install
cd ~
```

### 3. Configure nbfc for your laptop

```bash
sudo nbfc rate-config -a
```

Apply the best matching config (replace with your result):

```bash
sudo nbfc config --apply "HP 15 Notebook PC"
sudo nbfc start
```

### 4. Install acpi_call for EC access

```bash
sudo dnf install -y dkms kernel-devel
git clone https://github.com/nix-community/acpi_call.git
cd acpi_call
sudo make && sudo make install
sudo modprobe acpi_call
cd ~
```

### 5. Allow nbfc to run without password

```bash
sudo visudo -f /etc/sudoers.d/fancontrol
```

Add this line (replace `yourusername`):

```
yourusername ALL=(ALL) NOPASSWD: ALL
```

### 6. Clone this repo and set up the app

```bash
git clone https://github.com/ADITYA-TUMMURI/Hp-OMEN-cpu-fan-control.git
cd Hp-OMEN-cpu-fan-control
mkdir -p ~/.local/share/icons
cp fancontrol.svg ~/.local/share/icons/fancontrol.svg
cp fancontrol.desktop ~/.local/share/applications/
```

### 7. Auto-start nbfc on boot

```bash
echo 'sudo nbfc start' | sudo tee /etc/rc.d/rc.local
sudo chmod +x /etc/rc.d/rc.local
```

### 8. Run the app

```bash
sudo python3 fancontrol.py
```

Or search **Fan Control** in your app menu.

---

## Usage

| Action | How |
|---|---|
| Auto fan control | Click **AUTO** |
| Manual fan control | Click **MANUAL** → adjust slider → **APPLY** |
| Check temps | Shown live at the top |

---

## Notes

- **GPU fan** is locked by NVIDIA on laptop GPUs — cannot be controlled on Linux
- Set GPU fan curve from Windows once — settings persist in EC when booting Linux

---

## License

MIT
