# QR Generator Pro 🔲

A professional desktop QR code builder with **Dual-Mode** generation, live preview, custom colours, and logo embedding.

---

## Project Structure

```
QR_Generator_Pro/
│
├── assets/
│   ├── app_icon.ico          # Window icon (replace with your own)
│   └── logo_placeholder.png  # Default logo for testing
│
├── src/
│   ├── __init__.py
│   ├── generator.py          # Dual-mode QR engine
│   └── app_ui.py             # CustomTkinter UI
│
├── main.py                   # Entry point
├── requirements.txt
└── README.md
```

---

## Installation & Running (Development)

```bash
# 1. Create a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python main.py
```

---

## Features

| Feature | Details |
|---|---|
| **Simple QR Mode** | `ERROR_CORRECT_M` — 15% correction, cleaner & smaller |
| **Branded QR Mode** | `ERROR_CORRECT_H` — 30% correction, safe for logo overlay |
| **Live Preview** | Debounced 600 ms update while you type |
| **Custom Colours** | Pick any QR fill & background colour |
| **Logo Upload** | PNG / JPG logo centred on QR (Branded mode only) |
| **Save PNG / JPG** | Export at full resolution |
| **Dark / Light Mode** | Toggle in-app |

---

## Packaging to .exe (Windows)

```bash
# Step 1 — Install Nuitka
pip install nuitka

# Step 2 — Compile (run from project root)
python -m nuitka ^
  --standalone ^
  --onefile ^
  --enable-plugin=tk-inter ^
  --include-data-dir=assets=assets ^
  --windows-icon-from-ico=assets/app_icon.ico ^
  main.py
```

> **Note:** Replace `assets/app_icon.ico` with your own `.ico` file (256×256 recommended).  
> The compiled `.exe` will appear as `main.exe` in the same folder.

### Why Nuitka?
- **No Python required** on the target machine
- **Faster** startup than PyInstaller
- **Smaller** output compared to cx_Freeze

---

## Error Correction Modes Explained

| Mode | Level | Data recovery | Use case |
|---|---|---|---|
| `ERROR_CORRECT_M` | M — 15% | Up to 15% of codewords | Plain URLs, text |
| `ERROR_CORRECT_H` | H — 30% | Up to 30% of codewords | **Logo overlay** — the logo covers ~25% of the QR |

Always use **H** when embedding a logo. The extra redundancy ensures the QR still scans even with the centre obscured.

---

## Asset Path Resolution

`app_ui.py` uses a `resource_path()` helper that checks `sys._MEIPASS` first (set by Nuitka/PyInstaller when frozen) and falls back to the project root during development. This prevents asset-not-found crashes after packaging.

```python
def resource_path(relative: str) -> str:
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    if not getattr(sys, "frozen", False):
        base = os.path.join(base, "..")   # go up from src/
    return os.path.normpath(os.path.join(base, relative))
```
