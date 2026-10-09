"""Generate SVG section headings.

GitHub strips <style>, class, and inline <svg> from README markdown, so the
only way to put a chosen typeface on a heading is to ship it as an image.

Trade-off, stated plainly: image headings have no anchor links, so the README
outline on the GitHub page goes empty. The alt text carries the word for
screen readers.
"""

import base64
import pathlib

import generate_stats as G

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "hd"
INK = "#39FF14"
RULE = "#1A2B1A"
W = 900
H = 62


def heading(text: str) -> str:
    b64 = base64.b64encode(
        (ROOT / "fonts" / "headings.woff2").read_bytes()
    ).decode("ascii")
    face = "data:font/woff2;base64," + b64
    label = text.lower()
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" aria-label="{G.esc(text)}">'
        f"<style>@font-face{{font-family:'JBMono';src:url({face}) "
        f"format('woff2');font-weight:700;font-style:normal;font-display:swap}}"
        f"text{{font-family:'JBMono',monospace;fill:{INK}}}"
        f"line{{stroke:{RULE};stroke-width:1}}</style>"
        f'<text x="0" y="42" font-size="30" font-weight="700" '
        f'xml:space="preserve">{G.esc(label)}</text>'
        f'<line x1="0" y1="56" x2="{W}" y2="56"/>'
        f"</svg>"
    )


HEADINGS = [
    "whoami",

    "expertise",
    "projects",
    "approach",
    "connect",
]


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for slug in HEADINGS:
        p = OUT / f"{slug}.svg"
        p.write_text(heading(slug), encoding="utf-8")
        print(f"hd/{slug}.svg  {p.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
