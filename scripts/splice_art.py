"""Splice the braille banner into the previous README.

Surgical: takes README.md from HEAD~1 verbatim and replaces only the
portrait <img> line with the art block. Every other byte is untouched, so
none of the wording, sections, or SVG references change.
"""

import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
ART = ROOT / "assets" / "banner.txt"
README = ROOT / "README.md"

prev = subprocess.run(
    ["git", "show", "HEAD~1:README.md"],
    cwd=ROOT, capture_output=True, text=True, check=True,
).stdout

art_block = ART.read_text(encoding="utf-8").rstrip("\n")

old_img = '<img src="./portrait.svg" width="460" alt="Self-typing ASCII portrait of Bharadwaja Reddy" />'
assert old_img in prev, "portrait img line not found in HEAD~1 README"

new = prev.replace(old_img, "<pre>\n" + art_block + "\n</pre>", 1)

README.write_text(new, encoding="utf-8")

# verify: everything except that one line is identical
old_lines = prev.splitlines()
new_lines = new.splitlines()
removed = [l for l in old_lines if l not in new_lines]
added = [l for l in new_lines if l not in old_lines]
print(f"removed {len(removed)} line(s): {removed}")
print(f"added   {len(added)} line(s) (art + <pre> tags)")
print(f"length: {len(prev)} -> {len(new)} bytes")

# confirm art round-tripped intact
back = README.read_text(encoding="utf-8")
block = back.split("<pre>\n", 1)[1].split("\n</pre>", 1)[0]
src = art_block.rstrip("\n")
print("art byte-identical to assets/banner.txt:", block == src)
print("art lines:", len(block.splitlines()))
bad = {c for c in block if not (0x2800 <= ord(c) <= 0x28FF or ord(c) == 32)}
print("non-braille chars in art:", bad or "none")
print("portrait.svg still referenced:", "portrait.svg" in back)
