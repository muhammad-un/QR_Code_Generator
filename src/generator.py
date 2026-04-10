"""
generator.py — Dual-Mode QR Generation Engine
Handles Standard Mode and Logo (Branded) Mode with proper error correction.
"""

import qrcode
from qrcode.constants import ERROR_CORRECT_M, ERROR_CORRECT_H
from PIL import Image
import io


def generate_standard_qr(
    data: str,
    fill_color: str = "black",
    back_color: str = "white",
    box_size: int = 10,
    border: int = 4,
) -> Image.Image:
    """
    Standard Mode — ERROR_CORRECT_M (15% correction).
    Produces a cleaner, less dense QR code for plain URLs/text.
    """
    if not data.strip():
        raise ValueError("QR data cannot be empty.")

    qr = qrcode.QRCode(
        version=None,          # auto-select smallest version
        error_correction=ERROR_CORRECT_M,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color=fill_color, back_color=back_color)
    return img.convert("RGBA")


def generate_logo_qr(
    data: str,
    logo_path: str,
    fill_color: str = "black",
    back_color: str = "white",
    box_size: int = 10,
    border: int = 4,
    logo_ratio: float = 0.28,
) -> Image.Image:
    """
    Logo (Branded) Mode — ERROR_CORRECT_H (30% correction).
    Forces high error correction so the QR still scans after
    a logo is pasted over the center.

    logo_ratio: fraction of QR width the logo occupies (max ~0.30).
    """
    if not data.strip():
        raise ValueError("QR data cannot be empty.")

    # --- Build QR with HIGH error correction ---
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color=fill_color, back_color=back_color).convert("RGBA")

    # --- Paste logo in center ---
    try:
        logo = Image.open(logo_path).convert("RGBA")
    except Exception as exc:
        raise FileNotFoundError(f"Cannot open logo: {logo_path}") from exc

    qr_w, qr_h = qr_img.size
    max_logo_size = int(min(qr_w, qr_h) * logo_ratio)

    # Maintain aspect ratio
    logo_w, logo_h = logo.size
    scale = min(max_logo_size / logo_w, max_logo_size / logo_h)
    new_w = int(logo_w * scale)
    new_h = int(logo_h * scale)
    logo = logo.resize((new_w, new_h), Image.LANCZOS)

    # Add a white rounded padding box behind the logo
    pad = 8
    box_img = Image.new("RGBA", (new_w + pad * 2, new_h + pad * 2), (255, 255, 255, 240))
    box_img.paste(logo, (pad, pad), logo)

    paste_x = (qr_w - box_img.width) // 2
    paste_y = (qr_h - box_img.height) // 2
    qr_img.paste(box_img, (paste_x, paste_y), box_img)

    return qr_img


def pil_to_bytes(img: Image.Image, fmt: str = "PNG") -> bytes:
    """Convert a PIL image to raw bytes (for saving or embedding in UI)."""
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()
