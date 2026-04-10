"""
main.py — Entry point for QR Generator Pro
Run:  python main.py
"""

import sys
import os

# Ensure src/ is on the path when running as a script
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app_ui import QRApp


def main():
    app = QRApp()
    app.mainloop()


if __name__ == "__main__":
    main()
