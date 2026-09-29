"""Build the subsetted woff2 ramps used by the generated SVGs.

Subset per role, as the guide requires: inlining a full TTF into each file
would be ~4.5 MB across the page; subsets total ~57 KB.

    python scripts/build_fonts.py
"""

import pathlib
import sys

from fontTools import subset

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONTS = ROOT / "fonts"

# 13 ramp characters, leading space included. Built by codepoint so no shell
# quoting or editor can mangle the backtick.
RAMP_CHARS = " .`" + chr(58) + "-=+*cs#%@"
HEADING_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 &/.,:;-'\"()[]#|+*<>"
LATIN_CHARS = (
    "".join(chr(c) for c in range(0x20, 0x7F))
)

JOBS = [
    ("JetBrainsMono-Regular.ttf", RAMP_CHARS, "ramp.woff2"),
    ("JetBrainsMono-Bold.ttf", HEADING_CHARS, "headings.woff2"),
    ("JetBrainsMono-Regular.ttf", LATIN_CHARS, "basic-regular.woff2"),
    ("JetBrainsMono-Bold.ttf", LATIN_CHARS, "basic-bold.woff2"),
]


def build(src_name: str, text: str, out_name: str) -> None:
    src = FONTS / src_name
    out = FONTS / out_name
    if not src.exists():
        sys.exit(f"missing source font: {src}")

    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = []
    opts.hinting = False
    opts.desubroutinize = True
    opts.notdef_outline = True
    opts.recalc_bounds = True

    font = subset.load_font(str(src), opts)
    subsetter = subset.Subsetter(options=opts)
    subsetter.populate(text=text)
    subsetter.subset(font)
    subset.save_font(font, str(out), opts)
    print(f"{out_name:20} {len(text):4} chars  {out.stat().st_size:>7,} bytes")


def main() -> None:
    for src, text, out in JOBS:
        build(src, text, out)
    print("\nLicence: JetBrains Mono is SIL OFL 1.1 - ship the licence file.")


if __name__ == "__main__":
    main()
