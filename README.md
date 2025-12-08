# Win-Aura Monitor

> **Make your system pulse.**
>
> An immersive, minimalist, and non-intrusive system performance monitor for Windows. It visualizes resource usage directly on your active window's border.

![License](https://img.shields.io/badge/license-MIT-blue.svg) ![Python](https://img.shields.io/badge/python-3.8+-yellow.svg) ![Platform](https://img.shields.io/badge/platform-Windows-0078D6.svg)

[🇨🇳 中文版](README_ZH.md)

**Win-Aura** turns the border of your currently focused window into a real-time performance dashboard. Instead of checking Task Manager, simply glance at the border's **color** (RAM usage) and **breathing speed** (CPU usage) to intuitively sense your system's load.

## ✨ Features

* **🧘‍♂️ Zen Mode (Focus Assist)**
    * **Toggle via `F8`**: Instantly dims the entire screen background, highlighting *only* your active window.
    * **Smart Mask**: Automatically hides when accessing the Desktop or Start Menu to preserve usability.

* **🧠 RAM Visualization (Color Mapping)**
    * The border color shifts dynamically based on the process's RAM usage.
    * **White/Cyan:** Low load (Idle).
    * **Yellow/Orange:** Medium load.
    * **Red:** High load (Critical).
    * *Fully customizable thresholds.*

* **🫀 CPU Breathing (Animation)**
    * The "breathing" rate of the glow indicates CPU activity.
    * **Leisure Mode:** Slow, calm breathing when idle.
    * **Performance Mode:** Rapid flashing when the CPU is under heavy load.

* **🛡️ Smart Filtering & Anti-Flash**
    * **Zero Distraction:** Automatically ignores the Taskbar, Desktop, Start Menu, Notification Center, and Tray Overflow menus.
    * **Explorer Whitelist:** Only draws on actual File Explorer windows, ignoring system dialogs and properties windows.
    * **PID-Locking:** Prevents "ghost borders" from flashing on system windows during rapid context switching.

* **⚡ Native Performance**
    * **DWM Integration:** Uses `dwmapi.dll` to detect the exact visual bounds of Windows 11 rounded windows.
    * **Click-Through:** Uses `WS_EX_TRANSPARENT` to ensure the overlay captures no mouse events.

## 🛠️ Installation

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/YourUsername/Win-Aura.git](https://github.com/YourUsername/Win-Aura.git)
    cd Win-Aura
    ```

2.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run**
    ```bash
    python main.py
    ```

## ⚙️ Configuration

Win-Aura is designed to be hackable. You can tweak the aesthetic in the top section of `main.py`:

```python
# User Configuration
BORDER_WIDTH = 4           # Thickness in pixels
GLOW_LAYERS = 4            # Bloom intensity
RAM_SENSITIVITY_CAP = 10.0 # % of total RAM to trigger "Red" state

# Zen Mode
ZEN_MODE_ALPHA = 180       # Mask opacity (0-255)
ZEN_TOGGLE_KEY = 0x77      # F8 Key (win32con.VK_F8)

# Color Map (Threshold 0.0-1.0 -> RGB)
COLOR_STOPS = [
    (0.0,  (255, 255, 255)), # Idle
    (1.0,  (255, 0, 0))      # Critical
]
```

## 📄 License

This project is licensed under the MIT License.
