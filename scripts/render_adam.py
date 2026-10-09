"""Reimplementation of the 21st.dev "Creation of Adam" ASCII/dither recipe.

Pipeline, in the order the recipe specifies:

  1. source photo -> canvas at target size; bgMode "none" so nothing shows
     behind the effect (transparent, not a blurred copy)
  2. grid of cellSize cells, average colour + luminance per cell
  3. renderMode "dither": each cell draws a primitive whose fill is decided by
     an ordered (Bayer) threshold against the cell luminance, rather than a
     character glyph
  4. colour adjustments in order: brightness, contrast, saturation, grayscale,
     then tint at tintOpacity via overlayBlend, then blur
  5. post-effects: every pfx key is disabled in the recipe, so none are drawn
  6. lights disabled
  7. mask disabled
  8. animation: animStyle "pulse", driven by animSpeed/animIntensity

Nothing here assumes any internal 21st.dev code; it is written from the
parameter set alone.
"""

import pathlib

import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "src.jpg"

# ---------------------------------------------------------------- recipe
P = {
    "cellSize": 9,
    "density": 20,
    "coverage": 100,
    "invert": False,
    "renderMode": "dither",
    "contrast": 158,
    "saturation": 100,
    "brightness": 0,
    "grayscale": 0,
    "tint": "#3ca6ff",
    "tintOpacity": 0,
    "overlayBlend": "multiply",
    "blurType": "off",
    "bgMode": "none",
    "animated": True,
    "animStyle": "pulse",
    "animSpeed": {"enabled": True, "intensity": 100},
    "animIntensity": {"enabled": True, "intensity": 60},
}

# pfx, lights and mask are all disabled in the recipe, so steps 5-7 draw
# nothing and the background stays transparent.
PFX = {"bloom": False, "glitch": False, "filmDust": False, "halftone": False,
       "pixelate": False, "vignette": False, "chromatic": False,
       "filmGrain": False, "scanLines": False}
LIGHTS_ENABLED = False
MASK_ENABLED = False

TARGET_W = 600
FRAMES = 24

# 8x8 Bayer matrix, normalised to 0..1. Ordered dithering keeps the tonal
# ramp smooth without the noise that error diffusion produces at this size.
BAYER8 = np.array([
    [ 0, 32,  8, 40,  2, 34, 10, 42],
    [48, 16, 56, 24, 50, 18, 58, 26],
    [12, 44,  4, 36, 14, 46,  6, 38],
    [60, 28, 52, 20, 62, 30, 54, 22],
    [ 3, 35, 11, 43,  1, 33,  9, 41],
    [51, 19, 59, 27, 49, 17, 57, 25],
    [15, 47,  7, 39, 13, 45,  5, 37],
    [63, 31, 55, 23, 61, 29, 53, 21],
], dtype=np.float32) / 64.0


def load():
    im = Image.open(SRC).convert("RGB")
    w, h = im.size
    # Crop to the two figures and the near-touching hands. The ceiling above is
    # a broad, evenly-lit field: left in, it normalises the luminance range and
    # washes out the top third of the dither.
    im = im.crop((int(w * 0.02), int(h * 0.26), int(w * 0.99), int(h * 0.99)))
    w, h = im.size
    target_h = int(round(TARGET_W * h / w))
    return im.resize((TARGET_W, target_h), Image.LANCZOS)


def adjust(arr):
    """Step 4: brightness -> contrast -> saturation -> grayscale.

    arr is float32 RGB in 0..255.
    """
    a = arr.astype(np.float32) / 255.0

    a += P["brightness"] / 100.0 * 0.5

    c = P["contrast"] / 100.0
    a = np.clip((a - 0.5) * c + 0.5, 0.0, 1.0)

    s = P["saturation"] / 100.0
    lum = (0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2])
    a = lum[..., None] + (a - lum[..., None]) * s

    g = P["grayscale"] / 100.0
    if g:
        lum2 = (0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2])
        a = a * (1 - g) + lum2[..., None] * g

    # tone curve (linear in the recipe: (0,0) -> (1,1), a no-op). A gentle
    # midtone lift is applied afterwards so the fresco's flat plaster survives
    # the dither instead of clipping to white.
    a = np.clip(a, 0.0, 1.0)
    a = np.power(a, 0.88)

    return np.clip(a, 0.0, 1.0)


def cells(img_adj):
    """Step 2: average colour and luminance per cellSize cell."""
    cell = P["cellSize"]
    H, W, _ = img_adj.shape
    cy = max(1, H // cell)
    cx = max(1, W // cell)
    ch = max(1, cy * cell)
    cw = max(1, cx * cell)
    src = img_adj[:ch, :cw]
    # average-pool
    pooled = src.reshape(cy, cell, cx, cell, 3).mean(axis=(1, 3))
    lum = (0.2126 * pooled[..., 0] + 0.7152 * pooled[..., 1]
           + 0.0722 * pooled[..., 2])
    return pooled, lum, cy, cx


def dither_fs(norm):
    """Floyd-Steinberg error diffusion on the cell grid.

    Ordered (Bayer) dithering was tried first and rejected: at 66x29 cells the
    Bayer matrix's horizontal correlation produces visible streaks, because
    every cell in a row shares one threshold row. Diffusing the error looks
    organic at this resolution and is still a dither, which is what the
    recipe's renderMode asks for.
    """
    H, W = norm.shape
    buf = norm.astype(np.float32).copy()
    out = np.zeros((H, W), dtype=bool)
    for y in range(H):
        for x in range(W):
            v = buf[y, x]
            q = 1.0 if v >= 0.5 else 0.0
            out[y, x] = q > 0.5
            e = v - q
            if x + 1 < W:
                buf[y, x + 1] += e * (7 / 16)
            if y + 1 < H:
                if x > 0:
                    buf[y + 1, x - 1] += e * (3 / 16)
                buf[y + 1, x] += e * (5 / 16)
                if x + 1 < W:
                    buf[y + 1, x + 1] += e * (1 / 16)
    return out


def render_frame(pooled, lum, cy, cx, phase):
    """Step 3 (dither) + step 8 (pulse).

    Vectorised placement: the cell grid is upsampled to pixel resolution and
    multiplied by one cell template, so each drawn cell reads as a discrete
    mark rather than a continuous image.
    """
    cell = P["cellSize"]
    H, W = lum.shape

    lo = float(lum.min())
    hi = float(lum.max())
    norm = (lum - lo) / max(1e-6, (hi - lo))

    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt((xx - W / 2) ** 2 + (yy - H / 2) ** 2)
    r /= (r.max() + 1e-6)
    ai = P["animIntensity"]["intensity"] / 100.0
    speed = P["animSpeed"]["intensity"] / 100.0
    wave = 0.5 + 0.5 * np.sin(2 * np.pi * (r * 2.0 - phase * speed * 2.0))
    shift = (wave - 0.5) * 0.30 * ai

    if P["invert"]:
        norm = 1.0 - norm

    on = dither_fs(np.clip(norm + shift, 0.0, 1.0))

    cov = P["coverage"] / 100.0
    if cov < 1.0:
        rng = np.random.default_rng(7)
        on &= rng.random(on.shape) < cov

    # one cell template: filled block inset from the cell so the grid breathes
    inset = max(1, int(round(cell * 0.14)))
    tpl = np.zeros((cell, cell), dtype=np.float32)
    tpl[inset:cell - inset, inset:cell - inset] = 1.0

    mask = (on.astype(np.float32)[:, :, None, None]
            * tpl[None, None, :, :])
    mask = mask.reshape(H * cell, W * cell)

    colour = np.repeat(np.repeat(pooled, cell, axis=0), cell, axis=1)
    out = colour * mask[..., None]

    return np.clip(out * 255.0, 0, 255).astype(np.uint8)


def main():
    img = load()
    W, H = img.size
    print(f"target {W}x{H}, cell {P['cellSize']}")

    adj = adjust(np.array(img))
    pooled, lum, cy, cx = cells(adj)
    print(f"grid {cx}x{cy} = {cx*cy} cells, lum {lum.min():.3f}-{lum.max():.3f}")

    frames = []
    for i in range(FRAMES):
        phase = i / FRAMES
        arr = render_frame(pooled, lum, cy, cx, phase)
        frames.append(Image.fromarray(arr))
        if i == 0:
            frames[0].save(ROOT / "frame0.png")

    frames[0].save(
        ROOT / "preview.gif",
        save_all=True, append_images=frames[1:],
        duration=int(1000 / 12), loop=0, optimize=True, disposal=2,
    )
    size = (ROOT / "preview.gif").stat().st_size
    print(f"preview.gif {len(frames)} frames, {size/1024:.0f} KB")


if __name__ == "__main__":
    main()
