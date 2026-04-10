# QR Code Generator Pro 🔲

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![UI Library](https://img.shields.io/badge/UI-CustomTkinter-orange)](https://github.com/TomSchimansky/CustomTkinter)
[![License](https://img.shields.io/badge/license-MIT-green)](https://opensource.org/licenses/MIT)

A professional desktop application for generating customizable QR codes. Features dual-mode generation (Standard & Branded), real-time previews, and logo embedding.

---

## 🚀 Key Features

* **Dual-Mode Engine:** Toggle between clean "Simple" codes and robust "Branded" codes.
* **Logo Embedding:** Automatic scaling and white-padding for logos in Branded mode.
* **Live Preview:** Intelligent 600ms debounced preview updates as you type.
* **High-Resolution Export:** Save your designs as PNG or JPG.
* **Modern UI:** Built with CustomTkinter for a sleek, dark-themed experience.
* **Portable:** Optimized for Nuitka packaging into a single `.exe`.

---

## 📂 Project Structure

```text
QR_Code_Generator/
├── assets/
│   ├── app_icon.ico          # Application taskbar/window icon
│   └── logo_placeholder.png  # Sample logo for testing
├── src/
│   ├── generator.py          # Logic: QR Engine (Error Correction & Scaling)
│   └── app_ui.py             # View: CustomTkinter GUI & Event Handling
├── main.py                   # Controller: Application Entry Point
├── requirements.txt          # Project dependencies
└── README.md                 # Documentation

---
## 🛠️ Installation & Usage

1. **Clone the repository**
   ```bash
   git clone https://github.com/muhammad-un/QR_Code_Generator.git
   cd QR_Code_Generator

Create virtual environment (recommended)bash

python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate # macOS/Linux

Install dependencies & runbash

pip install -r requirements.txt
python main.py

 Building the Windows ExecutableThis project is optimized for Nuitka:bash

python -m nuitka --standalone --onefile --enable-plugin=tk-inter \
  --include-data-dir=assets=assets \
  --windows-icon-from-ico=assets/app_icon.ico \
  --output-filename=QR_Code_Generator_Pro main.py

 Technical OverviewError Correction StrategyThe app balances "cleanliness" and "reliability":Mode
Error Correction
Data Recovery
Use Case
Simple
Low (~15%)
Standard
Clean URLs and text
Branded
High (~30%)
Robust
With logo overlays

Asset Management (Important for .exe)To avoid "File Not Found" errors after packaging:python

def resource_path(relative: str) -> str:
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    if not getattr(sys, "frozen", False):
        base = os.path.join(base, "..")
    return os.path.normpath(os.path.join(base, relative))

 ContributingFeel free to fork this project, submit PRs, or report issues. Final Tip: Clean Git HistoryCreate a .gitignore file with this content:gitignore

__pycache__/
.venv/
build/
*.dist/
*.onefile-build/
*.exe

