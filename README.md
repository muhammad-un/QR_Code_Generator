# QR Code Generator Pro 🔲

[![Python Version](https://img.shields.io/badge/python-3.13%2B-blue)](https://www.python.org/)
[![UI Library](https://img.shields.io/badge/UI-CustomTkinter-orange)](https://github.com/TomSchimansky/CustomTkinter)
[![Build Tool](https://img.shields.io/badge/Build-Nuitka-green)](https://nuitka.net/)

A professional, high-performance desktop application for generating customizable QR codes. Designed with a modular architecture, it supports standard data encoding and branded QR codes with centered logos.

---

## 🚀 Key Features

* **Dual-Mode Engine:** * **Simple Mode:** Optimized for clean, low-density codes using `ERROR_CORRECT_M`.
    * **Branded Mode:** Uses `ERROR_CORRECT_H` (30% redundancy) to ensure scanability even when a logo is overlaid.
* **Custom Branding:** Support for logo uploads with automatic resizing and white-padding for high visibility.
* **Color Customization:** Pick any HEX color for the QR foreground and background.
* **Modern UI:** A sleek, responsive dark-mode interface built with **CustomTkinter**.
* **Threaded Generation:** QR codes are generated in the background to keep the UI smooth and lag-free.
* **High-Res Export:** Save designs as PNG or JPG for print-ready quality.

---

## 📂 Project Structure

The project follows a clean **MVC-lite** (Model-View-Controller) design to separate logic from the interface:

```text
QR_Code_Generator/
├── assets/
│   ├── app_icon.ico          # Application taskbar/window icon
│   └── logo_placeholder.png  # Default logo for testing
├── src/
│   ├── generator.py          # Backend logic: QR encoding & Image processing
│   └── app_ui.py             # Frontend: UI Layout, events, and state
├── main.py                   # Entry point: Application bootstrap
├── requirements.txt          # Dependency manifest
└── README.md                 # Project documentation
🛠️ Installation & Development1. PrerequisitesEnsure you have Python 3.13 installed (Stable version recommended for Nuitka builds).2. Setup EnvironmentBashpython -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
3. Run LocallyBashpython main.py
🏗️ Production Packaging (Standalone .exe)This project is optimized for Nuitka. Unlike PyInstaller, Nuitka compiles Python to C++ for a faster and more secure executable.Build Command:Bashpython -m nuitka --standalone --onefile --enable-plugin=tk-inter --windows-console-mode=disable --include-data-dir=assets=assets --windows-icon-from-ico=assets/app_icon.ico --output-filename=QR_Generator_Pro main.py
🧠 Technical SpecificationsError Correction StrategyModeEC LevelRecovery CapacityPurposeSimpleM~15%Standard URLs, clean look, faster scans.BrandedH~30%Essential for logo overlays to prevent scan failure.Dynamic Path HandlingTo ensure the app finds icons and assets regardless of where the .exe is placed, we use a robust resource_path helper:Pythondef resource_path(relative: str) -> str:
    import sys, os
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    if not getattr(sys, "frozen", False):
        base = os.path.join(base, "..")
    return os.path.normpath(os.path.join(base, relative))
🤝 ContributingFork the Project.Create your Feature Branch (git checkout -b feature/NewFeature).Commit your Changes.Push to the Branch.Open a Pull Request.📄 LicenseDistributed under the MIT License. See LICENSE for more information.
***

### 💡 Pro-Tip for your GitHub
Since you just pushed a lot of files, make sure your **`.gitignore`** is working. If you see folders like `main.dist` or `main.build` on GitHub, run these commands to clean it up:

```powershell
git rm -r --cached main.dist main.build main.onefile-build
git commit -m "Cleanup: remove build artifacts from repository"
git push origin main
