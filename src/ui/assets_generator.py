"""
Asset Generator for ProxyManager
Generates modern, anti-aliased, high-DPI assets:
- App Icons (PNG and multi-size ICO)
- Power Button states (Disconnected, Connected, Pulsing)
- Inno Setup Wizard Bitmaps (Large and Small)
- UI Icons
"""
import os
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def draw_glow(draw, center, radius, color, glow_width=20, max_alpha=120):
    cx, cy = center
    steps = 15
    for i in range(steps):
        r = radius + (glow_width * i // steps)
        alpha = int(max_alpha * (1 - (i / steps) ** 1.5))
        c = (color[0], color[1], color[2], alpha)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=c, width=2)


def generate_app_icon(output_dir: Path):
    """Generate 256x256 PNG and multi-resolution ICO"""
    size = 512  # Generate at 512 for crisp scaling
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = size // 2, size // 2

    # Outer rounded card / shield
    pad = 24
    radius = 110
    
    # Outer subtle glow
    for g in range(12):
        g_pad = pad - g * 2
        alpha = int(45 * (1 - g / 12))
        draw.rounded_rectangle(
            [g_pad, g_pad, size - g_pad, size - g_pad],
            radius=radius + g,
            outline=(16, 185, 129, alpha),
            width=2
        )

    # Card background (deep slate obsidian)
    draw.rounded_rectangle(
        [pad, pad, size - pad, size - pad],
        radius=radius,
        fill=(15, 23, 42, 255),  # Slate 900
        outline=(51, 65, 85, 255),  # Slate 700
        width=6
    )

    # Inner subtle circuit/gradient effect
    draw.rounded_rectangle(
        [pad + 12, pad + 12, size - pad - 12, size - pad - 12],
        radius=radius - 8,
        outline=(30, 41, 59, 255),
        width=3
    )

    # Outer glowing ring
    ring_r = 145
    draw_glow(draw, (cx, cy), ring_r, (16, 185, 129), glow_width=25, max_alpha=100)

    # Modern Emerald Power Ring
    ring_width = 24
    draw.ellipse(
        [cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r],
        outline=(16, 185, 129, 255),
        width=ring_width
    )

    # Top opening notch for power button
    notch_w = 46
    draw.rectangle([cx - notch_w // 2, cy - ring_r - 15, cx + notch_w // 2, cy - ring_r + 25], fill=(15, 23, 42, 255))

    # Power vertical bar
    bar_w = 22
    bar_top = cy - ring_r - 15
    bar_bottom = cy - 20
    draw.rounded_rectangle([cx - bar_w // 2, bar_top, cx + bar_w // 2, bar_bottom], radius=11, fill=(52, 211, 153, 255))

    # Center core glowing dot
    core_r = 40
    draw.ellipse([cx - core_r, cy - core_r, cx + core_r, cy + core_r], fill=(5, 150, 105, 255))
    core_inner = 24
    draw.ellipse([cx - core_inner, cy - core_inner, cx + core_inner, cy + core_inner], fill=(167, 243, 208, 255))

    # Save 256x256 PNG
    icon_256 = img.resize((256, 256), Image.Resampling.LANCZOS)
    icon_png_path = output_dir / "icon.png"
    icon_256.save(icon_png_path, "PNG")
    print(f"Generated {icon_png_path}")

    # Generate multi-size ICO (16, 24, 32, 48, 64, 128, 256)
    ico_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    icon_ico_path = output_dir / "icon.ico"
    icon_256.save(icon_ico_path, format="ICO", sizes=ico_sizes)
    print(f"Generated {icon_ico_path} with sizes {ico_sizes}")


def generate_power_buttons(output_dir: Path):
    """Generate high-res anti-aliased power buttons for UI"""
    size = 280  # Downscaled to 140x140 for Retina/High-DPI smoothness

    def create_button(connected=False, pulsing=False):
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        cx, cy = size // 2, size // 2

        if connected:
            base_r = 100
            # Ambient glow
            glow_w = 32 if pulsing else 24
            max_a = 150 if pulsing else 90
            draw_glow(draw, (cx, cy), base_r, (16, 185, 129), glow_width=glow_w, max_alpha=max_a)

            # Outer ring
            draw.ellipse(
                [cx - base_r, cy - base_r, cx + base_r, cy + base_r],
                fill=(16, 185, 129, 255),
                outline=(52, 211, 153, 255),
                width=4
            )

            # Inner gradient-like circle
            inner_r = 86
            draw.ellipse(
                [cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r],
                fill=(5, 150, 105, 255),
                outline=(110, 231, 183, 180),
                width=2
            )

            # Core circle
            center_r = 72
            draw.ellipse(
                [cx - center_r, cy - center_r, cx + center_r, cy + center_r],
                fill=(4, 120, 87, 255)
            )

            # Power Symbol (White / Mint)
            sym_r = 44
            sym_w = 10
            # Circle with gap
            draw.arc(
                [cx - sym_r, cy - sym_r, cx + sym_r, cy + sym_r],
                start=30, end=330,
                fill=(255, 255, 255, 255),
                width=sym_w
            )
            # Vertical line
            draw.line(
                [cx, cy - sym_r - 8, cx, cy - 6],
                fill=(255, 255, 255, 255),
                width=sym_w
            )
            # Dot in center
            dot_r = 8
            draw.ellipse([cx - dot_r, cy + 12 - dot_r, cx + dot_r, cy + 12 + dot_r], fill=(255, 255, 255, 255))

        else:
            base_r = 100
            # Subtle dark outer shadow
            draw_glow(draw, (cx, cy), base_r, (30, 41, 59), glow_width=16, max_alpha=60)

            # Outer base
            draw.ellipse(
                [cx - base_r, cy - base_r, cx + base_r, cy + base_r],
                fill=(30, 41, 59, 255),  # Slate 800
                outline=(51, 65, 85, 255),  # Slate 700
                width=3
            )

            # Inner surface
            inner_r = 86
            draw.ellipse(
                [cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r],
                fill=(15, 23, 42, 255),  # Slate 900
                outline=(51, 65, 85, 120),
                width=2
            )

            # Core
            center_r = 72
            draw.ellipse(
                [cx - center_r, cy - center_r, cx + center_r, cy + center_r],
                fill=(23, 31, 48, 255)
            )

            # Power Symbol (Muted Slate / Silver)
            sym_r = 44
            sym_w = 9
            draw.arc(
                [cx - sym_r, cy - sym_r, cx + sym_r, cy + sym_r],
                start=30, end=330,
                fill=(148, 163, 184, 255),
                width=sym_w
            )
            draw.line(
                [cx, cy - sym_r - 8, cx, cy - 6],
                fill=(148, 163, 184, 255),
                width=sym_w
            )

        # Scale down to 140x140
        return img.resize((140, 140), Image.Resampling.LANCZOS)

    btn_off = create_button(connected=False)
    btn_on = create_button(connected=True, pulsing=False)
    btn_pulse = create_button(connected=True, pulsing=True)

    btn_off.save(output_dir / "power_off.png", "PNG")
    btn_on.save(output_dir / "power_on.png", "PNG")
    btn_pulse.save(output_dir / "power_pulse.png", "PNG")
    print("Generated power button states (off, on, pulse)")


def generate_wizard_bitmaps(output_dir: Path):
    """Generate modern Inno Setup wizard bitmaps (BMP format)"""
    # 1. Wizard Large: 164 x 314
    w_large = Image.new('RGB', (164, 314), (11, 15, 23))  # Deep slate dark
    d_large = ImageDraw.Draw(w_large)

    # Gradient-like background lines
    for y in range(314):
        ratio = y / 314.0
        r = int(11 + 10 * ratio)
        g = int(15 + 25 * ratio)
        b = int(23 + 35 * ratio)
        d_large.line([(0, y), (164, y)], fill=(r, g, b))

    # Emerald glow accent blob at top
    for r in range(80, 0, -5):
        alpha = int(40 * (1 - r / 80))
        c = (16 + alpha, 185 - int(alpha * 0.5), 129 + alpha)
        d_large.ellipse([82 - r, 70 - r, 82 + r, 70 + r], outline=(16, 185, 129))

    # Draw logo circle
    d_large.ellipse([82 - 38, 70 - 38, 82 + 38, 70 + 38], fill=(15, 23, 42), outline=(16, 185, 129), width=3)
    # Power symbol
    d_large.arc([82 - 18, 70 - 18, 82 + 18, 70 + 18], start=30, end=330, fill=(52, 211, 153), width=4)
    d_large.line([82, 70 - 22, 82, 70 - 4], fill=(52, 211, 153), width=4)

    # Accent decorative lines
    d_large.line([20, 150, 144, 150], fill=(30, 41, 59), width=1)
    d_large.line([40, 155, 124, 155], fill=(16, 185, 129), width=2)
    d_large.line([20, 160, 144, 160], fill=(30, 41, 59), width=1)

    # Bottom decorative blocks
    d_large.rounded_rectangle([20, 200, 144, 270], radius=8, fill=(19, 28, 46), outline=(51, 65, 85), width=1)

    large_bmp_path = output_dir / "wizard_large.bmp"
    w_large.save(large_bmp_path, "BMP")
    print(f"Generated {large_bmp_path}")

    # 2. Wizard Small: 55 x 55
    w_small = Image.new('RGB', (55, 55), (15, 23, 42))
    d_small = ImageDraw.Draw(w_small)
    d_small.ellipse([6, 6, 48, 48], fill=(11, 15, 23), outline=(16, 185, 129), width=2)
    d_small.arc([16, 16, 38, 38], start=30, end=330, fill=(52, 211, 153), width=2)
    d_small.line([27, 13, 27, 23], fill=(52, 211, 153), width=2)

    small_bmp_path = output_dir / "wizard_small.bmp"
    w_small.save(small_bmp_path, "BMP")
    print(f"Generated {small_bmp_path}")


if __name__ == "__main__":
    assets_path = Path("D:/hwork/ProxyManager_backup_20260919_161319/assets")
    ensure_dir(assets_path)
    generate_app_icon(assets_path)
    generate_power_buttons(assets_path)
    generate_wizard_bitmaps(assets_path)
    print("All assets successfully generated!")
