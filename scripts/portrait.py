"""Self-typing ASCII portrait -> animated SVG.

Pipeline (per the ASCII Portrait README Guide, with the darkening-curve fix):
    rembg cut-out -> bilateral filter -> CLAHE -> (v/255)**1.7 -> ramp

Grid geometry is baked for JetBrains Mono at 0.600 em advance, so the font is
inlined as a subset woff2 data URI. Without this, Windows visitors (Consolas,
~0.55 advance) see the portrait ~7% too narrow.
"""

import base64
import math
import pathlib
import subprocess
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "fonts"
RAMP_WOFF2 = FONT_DIR / "ramp.woff2"

# 13 levels: the leading space clears the background to nothing.
RAMP = " .`:-=+*cs#%@"
COLS = 90
FONT_PX = 12.9
CHAR_W = 7.74  # 0.600 em, exact
ROW_H = FONT_PX * 0.48
DISPLAY_W = 460

INK = "#39FF14"  # neon green, matching the profile palette


def load_frame(src: pathlib.Path) -> Image.Image:
    """First frame of the source, as RGB."""
    im = Image.open(src)
    im.seek(0)
    return im.convert("RGB")


def cutout(im: Image.Image) -> Image.Image:
    """rembg removes the background; everything outside the subject becomes
    white, which maps to the blank end of the ramp. Skipping this fills the
    background with @ and drowns the portrait."""
    from rembg import remove

    out = remove(im)
    if not isinstance(out, Image.Image):
        buf = pathlib.Path(ROOT / ".cutout.png")
        buf.write_bytes(out)
        out = Image.open(buf)

    # rembg hands back RGBA. Force anything the model called background to pure
    # white: the ramp's blank end is white, so this is what clears the frame.
    if out.mode != "RGBA":
        out = out.convert("RGBA")
    alpha = out.split()[-1]

    # Guard against a bad mask: if the model kept almost everything, fall back
    # to a luminance key so the portrait is still legible.
    if np.array(alpha).mean() < 32 or np.array(alpha).mean() > 250:
        a = np.array(out.convert("L")).astype(np.int32)
        alpha = Image.fromarray(
            np.clip((a - 14) * 14, 0, 255).astype(np.uint8)
        )

    white = Image.new("RGB", out.size, (255, 255, 255))
    white.paste(out.convert("RGB"), mask=alpha)
    return white


def enhance(im: Image.Image) -> Image.Image:
    """bilateral smooths skin while keeping edges; CLAHE gives local contrast
    per tile so a flatly-lit face does not render as one tone; the darkening
    curve is the fix that makes glasses, brows and lips survive."""
    img = np.array(im.convert("L"))
    img = cv2.bilateralFilter(img, d=7, sigmaColor=40, sigmaSpace=7)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    img = clahe.apply(img)
    img = np.power(img.astype(np.float32) / 255.0, 1.7)
    return Image.fromarray((img * 255).astype(np.uint8))


def to_ascii(im: Image.Image, cols: int = COLS) -> list[str]:
    """Resize preserving aspect, then map luminance to the ramp.

    The ramp runs from blank (space) to dense (@), and the background is
    forced to white. So luminance is INVERTED here: white -> space, and the
    dark features of the portrait -> dense characters. Mapping it the other
    way floods the whole frame with @ and drowns the face.
    """
    w, h = im.size
    # target height from the character cell aspect, per the guide
    rows = max(1, int(cols * (h / w) * 0.48))
    small = im.resize((cols, rows), Image.LANCZOS)
    px = np.array(small)

    out = []
    top = len(RAMP) - 1
    for row in px:
        chars = []
        for v in row:
            idx = int(round((1.0 - (int(v) / 255.0)) * top))
            chars.append(RAMP[max(0, min(top, idx))])
        out.append("".join(chars))
    return out


def crop_face(im: Image.Image) -> Image.Image:
    """Tight crop so the face fills the frame. A face at 30% of frame gets too
    few characters across and the eyes will not resolve."""
    w, h = im.size
    side = int(min(w, h) * 0.92)
    left = max(0, (w - side) // 2)
    top = max(0, int((h - side) * 0.28))
    return im.crop((left, top, left + side, top + side))


def font_face_uri() -> str:
    if not RAMP_WOFF2.exists():
        sys.exit(
            f"missing {RAMP_WOFF2}\n"
            "build it with:\n"
            '  pyftsubset fonts/JetBrainsMono-Regular.ttf --text=" .`:-=+*cs#%@" '
            "--flavor=woff2 --layout-features='' --no-hinting -o fonts/ramp.woff2"
        )
    b64 = base64.b64encode(RAMP_WOFF2.read_bytes()).decode("ascii")
    return (
        "data:font/woff2;base64,"
        + b64
    )


def build_svg(lines: list[str]) -> str:
    rows = len(lines)
    w = int(COLS * CHAR_W)
    h = int(rows * ROW_H)
    face = font_face_uri()
    stagger = 0.09
    # whole portrait takes ~ rows*stagger seconds; last row starts at that point
    total = round(rows * stagger + 0.55, 2)

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" '
        f'aria-label="Self-typing ASCII portrait">'
    )
    parts.append("<style>")
    parts.append(
        "@font-face{font-family:'JBMono';src:url(" + face + ") format('woff2');"
        "font-weight:400;font-style:normal;font-display:block}"
    )
    parts.append(
        "text{font-family:'JBMono',monospace;fill:" + INK + ";"
        "white-space:pre;dominant-baseline:hanging}"
    )
    parts.append(".cursor{fill:" + INK + "}")
    parts.append("</style>")

    for i, line in enumerate(lines):
        begin = round(i * stagger, 3)
        y = round(i * ROW_H, 2)
        # The clip rect must be positioned at THIS row's own y. Leaving it at
        # y="0" means every row is clipped to the same 6px band at the top of
        # the image, so the portrait renders as an almost invisible sliver.
        #
        # The width attribute carries the FINAL value, not 0, so that if SMIL is
        # blocked or unsupported the clip is already fully open and the portrait
        # still renders - it simply does not animate.
        parts.append(
            f'<clipPath id="c{i}">'
            f'<rect x="0" y="{y}" height="{ROW_H}" width="{w}">'
            f'<animate attributeName="width" from="0" to="{w}" '
            f'dur="0.55s" begin="{begin}s" fill="freeze"/>'
            f"</rect></clipPath>"
        )
        parts.append(
            f'<text x="0" y="{y}" clip-path="url(#c{i})" '
            f'textLength="{w}" lengthAdjust="spacingAndGlyphs" '
            f'font-size="{FONT_PX}">{escape(line)}</text>'
        )

    parts.append("</svg>")
    return "".join(parts)


def escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main() -> None:
    src = ROOT / "source.gif"
    if not src.exists():
        sys.exit("source.gif missing")

    im = load_frame(src)
    im = crop_face(im)
    im = cutout(im)
    im = enhance(im)
    lines = to_ascii(im)

    out = ROOT / "portrait.svg"
    out.write_text(build_svg(lines), encoding="utf-8")
    print(f"{out} rows={len(lines)} bytes={out.stat().st_size}")


if __name__ == "__main__":
    main()
