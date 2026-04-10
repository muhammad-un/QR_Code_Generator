"""
app_ui.py — QR Generator Pro UI
Built with CustomTkinter. Features:
  • Dark/Light mode toggle
  • Simple / Branded mode switch with dynamic logo upload button
  • Live preview with debounced typing detection
  • Color picker for QR fill and background
  • Save to PNG / SVG
"""

import sys
import os
import threading
import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox

import customtkinter as ctk
from PIL import Image, ImageTk

# --- Locate assets safely (works both in dev and after Nuitka packaging) ---
def resource_path(relative: str) -> str:
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    # go one level up from src/ to project root when running normally
    if not getattr(sys, "frozen", False):
        base = os.path.join(base, "..")
    return os.path.normpath(os.path.join(base, relative))


# Import engine (works as a package and as a standalone)
try:
    from src.generator import generate_standard_qr, generate_logo_qr
except ImportError:
    from generator import generate_standard_qr, generate_logo_qr


# ──────────────────────────────────────────────
#  Colour palette (used by both themes)
# ──────────────────────────────────────────────
ACCENT   = "#1E90FF"   # dodger blue — primary action colour
SUCCESS  = "#2ECC71"
DANGER   = "#E74C3C"
SURFACE  = "#1C1F26"   # dark card surface


class QRApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ── Window setup ──────────────────────────────
        self.title("QR Generator Pro")
        self.geometry("960x680")
        self.minsize(820, 600)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Try to set window icon
        icon_path = resource_path("assets/app_icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

        # ── State variables ───────────────────────────
        self.qr_data_var  = tk.StringVar()
        self.mode_var     = tk.StringVar(value="simple")   # "simple" | "branded"
        self.fill_color   = "#000000"
        self.back_color   = "#FFFFFF"
        self.logo_path    = None
        self.current_qr   = None          # PIL Image
        self._debounce_id = None          # after() job id
        self.theme_dark   = True

        self._build_layout()
        self._bind_events()

    # ══════════════════════════════════════════════════
    #  Layout
    # ══════════════════════════════════════════════════
    def _build_layout(self):
        self.grid_columnconfigure(0, weight=0)   # left panel — fixed
        self.grid_columnconfigure(1, weight=1)   # right panel — expands
        self.grid_rowconfigure(0, weight=1)

        self._build_left_panel()
        self._build_right_panel()

    # ── Left control panel ────────────────────────────
    def _build_left_panel(self):
        lf = ctk.CTkFrame(self, width=340, corner_radius=0)
        lf.grid(row=0, column=0, sticky="nsew")
        lf.grid_propagate(False)
        lf.grid_rowconfigure(20, weight=1)   # spacer row

        pad = {"padx": 20, "pady": 6}

        # ── Header ──
        hdr = ctk.CTkLabel(lf, text="⬛ QR Generator Pro",
                            font=ctk.CTkFont("Courier", 18, "bold"))
        hdr.grid(row=0, column=0, sticky="w", padx=20, pady=(22, 4))

        ctk.CTkLabel(lf, text="Professional QR Code Builder",
                     font=ctk.CTkFont(size=12), text_color="gray").grid(
            row=1, column=0, sticky="w", padx=20, pady=(0, 16))

        # ── Mode toggle ──
        ctk.CTkLabel(lf, text="MODE", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="gray").grid(row=2, column=0, sticky="w", **pad)

        self.mode_seg = ctk.CTkSegmentedButton(
            lf,
            values=["Simple QR", "Branded QR"],
            command=self._on_mode_change,
            font=ctk.CTkFont(size=13),
            selected_color=ACCENT,
        )
        self.mode_seg.set("Simple QR")
        self.mode_seg.grid(row=3, column=0, sticky="ew", **pad)

        # ── Text / URL input ──
        ctk.CTkLabel(lf, text="TEXT / URL", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="gray").grid(row=4, column=0, sticky="w", **pad)

        self.data_entry = ctk.CTkTextbox(lf, height=90,
                                         font=ctk.CTkFont("Courier", 13),
                                         border_width=1)
        self.data_entry.grid(row=5, column=0, sticky="ew", **pad)

        # ── Logo upload (hidden by default) ──
        self.logo_frame = ctk.CTkFrame(lf, fg_color="transparent")
        self.logo_frame.grid(row=6, column=0, sticky="ew", **pad)
        self.logo_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.logo_frame, text="LOGO IMAGE",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="gray").grid(row=0, column=0, sticky="w", pady=(0, 4))

        self.logo_btn = ctk.CTkButton(
            self.logo_frame, text="📁  Upload Logo",
            command=self._pick_logo,
            fg_color="#2D3142", hover_color="#3D4152",
        )
        self.logo_btn.grid(row=1, column=0, sticky="ew")

        self.logo_label = ctk.CTkLabel(self.logo_frame, text="No logo selected",
                                        font=ctk.CTkFont(size=11), text_color="gray")
        self.logo_label.grid(row=2, column=0, sticky="w", pady=(4, 0))

        self.logo_frame.grid_remove()   # hidden initially

        # ── Colours ──
        ctk.CTkLabel(lf, text="COLOURS", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="gray").grid(row=7, column=0, sticky="w", **pad)

        colour_row = ctk.CTkFrame(lf, fg_color="transparent")
        colour_row.grid(row=8, column=0, sticky="ew", **pad)
        colour_row.grid_columnconfigure((0, 1), weight=1)

        self.fill_btn = ctk.CTkButton(colour_row, text="● QR Colour",
                                       fg_color=self.fill_color,
                                       command=self._pick_fill)
        self.fill_btn.grid(row=0, column=0, sticky="ew", padx=(0, 4))

        self.back_btn = ctk.CTkButton(colour_row, text="○ Background",
                                       fg_color="#555555",
                                       command=self._pick_back)
        self.back_btn.grid(row=0, column=1, sticky="ew", padx=(4, 0))

        # ── Generate button ──
        self.gen_btn = ctk.CTkButton(
            lf, text="⚡  Generate QR",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=44,
            fg_color=ACCENT,
            hover_color="#1565C0",
            command=self._generate,
        )
        self.gen_btn.grid(row=9, column=0, sticky="ew", padx=20, pady=(16, 4))

        # ── Save button ──
        self.save_btn = ctk.CTkButton(
            lf, text="💾  Save PNG",
            font=ctk.CTkFont(size=13),
            height=38,
            fg_color="#2D3142",
            hover_color="#3D4152",
            command=self._save_qr,
            state="disabled",
        )
        self.save_btn.grid(row=10, column=0, sticky="ew", padx=20, pady=4)

        # ── Theme toggle ──
        self.theme_btn = ctk.CTkButton(
            lf, text="☀  Light Mode",
            font=ctk.CTkFont(size=12),
            height=32,
            fg_color="transparent",
            border_width=1,
            text_color="gray",
            hover_color="#2D3142",
            command=self._toggle_theme,
        )
        self.theme_btn.grid(row=11, column=0, sticky="ew", padx=20, pady=(8, 0))

        # ── Status bar ──
        self.status_var = tk.StringVar(value="Ready — enter text to begin.")
        ctk.CTkLabel(lf, textvariable=self.status_var,
                     font=ctk.CTkFont(size=11),
                     text_color="gray",
                     wraplength=300).grid(row=12, column=0, sticky="w", padx=20, pady=(12, 20))

    # ── Right preview panel ───────────────────────────
    def _build_right_panel(self):
        rf = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=0)
        rf.grid(row=0, column=1, sticky="nsew")
        rf.grid_rowconfigure(0, weight=1)
        rf.grid_columnconfigure(0, weight=1)

        # Canvas area
        canvas_frame = ctk.CTkFrame(rf, fg_color="transparent")
        canvas_frame.grid(row=0, column=0)

        self.preview_label = ctk.CTkLabel(
            canvas_frame,
            text="Your QR code\nwill appear here",
            font=ctk.CTkFont("Courier", 15),
            text_color="#555555",
            width=480, height=480,
        )
        self.preview_label.grid(row=0, column=0, padx=40, pady=40)

        # Info strip at bottom
        self.info_label = ctk.CTkLabel(
            rf,
            text="",
            font=ctk.CTkFont("Courier", 11),
            text_color="#555555",
        )
        self.info_label.grid(row=1, column=0, pady=(0, 16))

    # ══════════════════════════════════════════════════
    #  Events & helpers
    # ══════════════════════════════════════════════════
    def _bind_events(self):
        # Live preview: debounce 600 ms after last keystroke
        self.data_entry.bind("<KeyRelease>", self._schedule_preview)

    def _schedule_preview(self, _event=None):
        if self._debounce_id:
            self.after_cancel(self._debounce_id)
        self._debounce_id = self.after(600, self._generate)

    def _on_mode_change(self, value: str):
        if value == "Branded QR":
            self.mode_var.set("branded")
            self.logo_frame.grid()
        else:
            self.mode_var.set("simple")
            self.logo_frame.grid_remove()

        # Re-generate if we already have data
        if self.data_entry.get("1.0", "end").strip():
            self._generate()

    def _pick_logo(self):
        path = filedialog.askopenfilename(
            title="Select Logo",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.webp"), ("All", "*.*")],
        )
        if path:
            self.logo_path = path
            fname = os.path.basename(path)
            self.logo_label.configure(text=f"✓ {fname[:30]}", text_color=SUCCESS)
            self._generate()

    def _pick_fill(self):
        color = colorchooser.askcolor(title="QR Code Colour", initialcolor=self.fill_color)
        if color and color[1]:
            self.fill_color = color[1]
            self.fill_btn.configure(fg_color=self.fill_color)
            self._generate()

    def _pick_back(self):
        color = colorchooser.askcolor(title="Background Colour", initialcolor=self.back_color)
        if color and color[1]:
            self.back_color = color[1]
            self._generate()

    def _toggle_theme(self):
        self.theme_dark = not self.theme_dark
        if self.theme_dark:
            ctk.set_appearance_mode("dark")
            self.theme_btn.configure(text="☀  Light Mode")
        else:
            ctk.set_appearance_mode("light")
            self.theme_btn.configure(text="🌙  Dark Mode")

    # ══════════════════════════════════════════════════
    #  Core: Generate & Preview
    # ══════════════════════════════════════════════════
    def _generate(self):
        data = self.data_entry.get("1.0", "end").strip()
        if not data:
            self.status_var.set("Enter text or URL above.")
            return

        self.gen_btn.configure(state="disabled", text="⏳  Generating…")
        self.status_var.set("Generating…")

        # Run in thread so UI stays responsive
        threading.Thread(target=self._do_generate, args=(data,), daemon=True).start()

    def _do_generate(self, data: str):
        try:
            mode = self.mode_var.get()
            if mode == "branded":
                if not self.logo_path:
                    self.after(0, lambda: self.status_var.set(
                        "⚠ Upload a logo first, or switch to Simple QR."))
                    self.after(0, lambda: self.gen_btn.configure(
                        state="normal", text="⚡  Generate QR"))
                    return
                img = generate_logo_qr(
                    data=data,
                    logo_path=self.logo_path,
                    fill_color=self.fill_color,
                    back_color=self.back_color,
                )
                mode_label = "Branded QR  •  Error Correction: H (30%)"
            else:
                img = generate_standard_qr(
                    data=data,
                    fill_color=self.fill_color,
                    back_color=self.back_color,
                )
                mode_label = "Simple QR  •  Error Correction: M (15%)"

            self.current_qr = img
            self.after(0, self._update_preview, img, mode_label)

        except Exception as exc:
            self.after(0, lambda: self.status_var.set(f"Error: {exc}"))
            self.after(0, lambda: self.gen_btn.configure(
                state="normal", text="⚡  Generate QR"))

    def _update_preview(self, img: Image.Image, mode_label: str):
        # Scale for display (max 460×460)
        display_size = 460
        thumb = img.copy()
        thumb.thumbnail((display_size, display_size), Image.NEAREST)

        ctk_img = ctk.CTkImage(light_image=thumb, dark_image=thumb,
                                size=(thumb.width, thumb.height))
        self.preview_label.configure(image=ctk_img, text="")
        self.preview_label._image = ctk_img   # keep reference

        # Status
        w, h = img.size
        self.status_var.set(f"✓ QR ready  |  {w}×{h} px")
        self.info_label.configure(text=mode_label)
        self.gen_btn.configure(state="normal", text="⚡  Generate QR")
        self.save_btn.configure(state="normal")

    # ══════════════════════════════════════════════════
    #  Save
    # ══════════════════════════════════════════════════
    def _save_qr(self):
        if not self.current_qr:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg")],
            title="Save QR Code",
        )
        if path:
            try:
                save_img = self.current_qr
                if path.lower().endswith(".jpg"):
                    save_img = save_img.convert("RGB")
                save_img.save(path)
                self.status_var.set(f"✓ Saved → {os.path.basename(path)}")
            except Exception as exc:
                messagebox.showerror("Save Error", str(exc))
