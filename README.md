<div align="center">

# 🌐 ProxyManager

### Modern, Ultra-Fast Windows Proxy Management Desktop Application

[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-blue.svg)](https://github.com/ali-aho/ProxyManager)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![UI](https://img.shields.io/badge/UI-CustomTkinter-emerald.svg)](https://github.com/TomSchimansky/CustomTkinter)
[![Open Source](https://img.shields.io/badge/Open%20Source-Yes%20%E2%99%A5-brightgreen.svg)](https://github.com/ali-aho/ProxyManager)
[![Issues](https://img.shields.io/badge/Issues-Welcome-green.svg)](https://github.com/ali-aho/ProxyManager/issues)

---

**[🇬🇧 English](README.md) • [🇮🇷 فارسی (Persian)](README.fa.md)**

---

</div>

**ProxyManager** is a modern, lightweight, open-source Windows application designed to manage, switch, and monitor your network proxy connections effortlessly. Built with Python, CustomTkinter, and Win32 APIs, it delivers a glassmorphism dark aesthetic, live connection metrics, and reliable system integration without annoying UAC popups or lagging console windows.

---

## ✨ Features

- **⚡ Instant Proxy Switching**: Directly toggles Windows system proxy settings via native registry operations (`HKCU`) without flashing `cmd.exe` windows or delay.
- **🎨 Modern Dark Aesthetic**: Custom-engineered UI with deep obsidian surfaces, emerald accents, responsive cards, and crisp high-DPI icons.
- **🛡️ Live State Synchronization**: Automatically detects changes in Windows system proxy settings in real-time, keeping the UI perfectly in sync.
- **📊 Real-Time Latency Ping**: Test connection response time to any proxy server with a single click before or during connection.
- **🔔 Docked In-App Notifications**: Sleek, non-intrusive notifications anchored neatly at the bottom-right corner of the application—no messy floating popups.
- **📂 Smart Profile Management**:
  - Add, edit, test, and delete proxy profiles with ease.
  - Search filter across profile names, hostnames, and ports.
  - Smart URL parser: Paste `127.0.0.1:8080` or `http://proxy.com:1080` directly and the host and port are separated automatically.
- **🚀 Safe Windows Startup**:
  - Run minimized in the system tray on Windows boot.
  - Optional auto-disable feature on PC startup to ensure dangling proxies don't block your connection.
- **📌 System Tray Support**: Keep ProxyManager running unobtrusively in the Windows taskbar tray.
- **🛠️ Built-in Diagnostics**:
  - One-click **Flush Windows Proxy** to restore direct internet connectivity if an unexpected disconnection occurs.
  - Instant launch for Windows native Proxy Settings using direct `ShellExecute` (zero cmd window).
- **📦 Customizable Inno Setup Installer**:
  - Clean installer supporting custom installation directory selection.
  - Complete, safe uninstallation that restores Windows proxy settings.

---

## 🚀 Active Maintenance & Community Support

> **⭐ We are committed to active development!**  
> This project is 100% open source and actively maintained. Every single **Issue**, **Bug Report**, and **Feature Request** on GitHub is reviewed and handled promptly. We release updates frequently to keep ProxyManager fast, reliable, and modern.

If ProxyManager helps you:
1. **Star ⭐ this repository** on GitHub to show your support!
2. **Follow [@ali-aho](https://github.com/ali-aho)** on GitHub to get notified of new releases and upcoming projects.
3. [Open an Issue](https://github.com/ali-aho/ProxyManager/issues) if you have an idea, suggestion, or bug report.

---

## 📥 Installation

### Method 1: Windows Installer (Recommended)
Download the latest `ProxyManager_Setup.exe` from the Releases page:
- Run the setup wizard.
- Choose any custom directory of your choice (e.g. `C:\Program Files\ProxyManager` or custom drive).
- Complete the installation and launch immediately without admin prompts.

### Method 2: Standalone Executable
You can download and run `ProxyManager.exe` directly as a standalone portable application.

---

## 🛠️ Running from Source

### Prerequisites
- Python 3.10, 3.11, 3.12, 3.13, or 3.14
- Windows 10 or Windows 11

### Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ali-aho/ProxyManager.git
   cd ProxyManager
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python src/main.py
   ```

---

## 🧪 Testing

The codebase includes comprehensive unit and integration tests covering configuration management and Windows proxy operations:

```bash
pytest tests
```

---

## 🔨 Building from Source

### 1. Build Standalone Executable (PyInstaller)
```bash
pyinstaller build_exe.spec --noconfirm
```
The output executable will be created at `dist/ProxyManager.exe`.

### 2. Build Inno Setup Installer
Ensure [Inno Setup 6](https://jrsoftware.org/isdl.php) is installed, then compile `setup.iss`:
```bash
iscc setup.iss
```
The installer will be generated at `dist/ProxyManager_Setup.exe`.

---

## 🤝 Contributing

Contributions, feature proposals, and pull requests are warmly welcome!
1. Fork the Project.
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the Branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.

Developed with ❤️ by **[ali-aho (VortexM)](https://github.com/ali-aho)**.
