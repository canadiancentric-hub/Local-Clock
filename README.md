# Local Clock (Offline)

A lightweight, highly customizable, and distro-agnostic desktop clock built with Python and Tkinter. This application is designed to run as a standalone AppImage, requiring no system-level dependencies or installation.

## 🛡️ Privacy & Security (Zero-Connectivity)
* **No Internet Required**: This application is strictly offline and does not require an internet connection to function.
* **Zero External Tracking**: There are no telemetries, analytics, or external API calls.
* **Local Data**: All settings are stored locally in a JSON file within your home directory.

## 🔑 System Permissions & Access
To maintain its lightweight footprint, the application only requires the following:
* **System Time Access**: Reads the local hardware clock to provide accurate time.
* **File System**: Permission to write to its own settings file for saving preferences (colors, offsets, etc.).
* **Display**: Access to the windowing system (X11/Wayland) for the GUI.

## ✨ Key Features
* **Multi-Clock & Offset Features**: Launch multiple instances simultaneously, each with independent time settings.
* **Custom Time Offsets**: Manually adjust time by hours or minutes—perfect for tracking different time zones.
* **One-Click Resync**: Instantly snap back to precise system time using the "Resync to Computer" button.
* **Drift-Free Precision**: Internal logic prevents software lag by re-syncing with the system clock every minute.
* **Persistent Settings**: Automatically saves preferences (color, format, position) to a local JSON file with automated backups.
* **Portable AppImage**: Self-contained binary verified to work across different Linux distributions (tested on Mint and Fedora).

## 🛠️ Technical Overview
The project is structured into three main modules:
1. **`main.py`**: Handles the GUI lifecycle and event binding.
2. **`clock_logic.py`**: Manages the time-keeping engine and calculates offsets.
3. **`settings_manager.py`**: Manages a safe-write system for user configurations.

## 🚀 Installation & Usage
1. Download `Local_Clock_Offline.AppImage`.
2. Make it executable: `chmod +x Local_Clock_Offline.AppImage`.
3. Double-click to launch.

## 📄 License
This project is licensed under the **MIT License**.

## ☕ Support
If you find this tool useful, consider supporting the project:

