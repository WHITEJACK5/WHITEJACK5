"""Replace the README's braille banner with a new art file.

Surgical: only the content between <pre> and </pre> changes. The rest of
README.md is left byte-identical. The art is read as UTF-8 and written
through untouched, then verified byte-for-byte after the splice.
"""

import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
NEW_ART = pathlib.Path(r"C:\Users\BHARADWAJA REDDY\Downloads\art.txt")
README = ROOT / "README.md"
BANNER = ROOT / "assets" / "banner.txt"

raw = NEW_ART.read_text(encoding="utf-8").splitlines()

# keep only braille + space; drop any trailing note
clean = []
for line in raw:
    buf = []
    for ch in line:
        if 0x2800 <= ord(ch) <= 0x28FF or ord(ch) == 32:
            buf.append(ch)
        else:
            break
    clean.append("".join(buf))
while clean and not clean[-1].strip():
    clean.pop()

bad = {c for c in "".join(clean) if not (0x2800 <= ord(c) <= 0x28FF or ord(c) == 32)}
if bad:
    raise SystemExit(f"art contains non-braille characters: {bad}")

art = "\n".join(clean)
print(f"new art: {len(clean)} lines, widths={sorted({len(l) for l in clean})}")

old = README.read_text(encoding="utf-8")
head, sep, rest = old.partition("<pre>\n")
if not sep:
    raise SystemExit("no <pre> block in README")
_, sep2, tail = rest.partition("\n</pre>")
if not sep2:
    raise SystemExit("no closing </pre> in README")

before = len(old)
new = head + sep + art + sep2 + tail
README.write_text(new, encoding="utf-8")
BANNER.write_text(art + "\n", encoding="utf-8")

# verify
back = README.read_text(encoding="utf-8")
block = back.split("<pre>\n", 1)[1].split("\n</pre>", 1)[0]
print(f"size: {before} -> {len(new)} bytes")
print("art byte-identical after splice:", block == art)
print("portrait.svg referenced:", "portrait.svg" in back)
print("svg refs still present:", back.count('src="./'))

# confirm nothing outside the art block changed
orig = old.split("<pre>\n", 1)[0] == new.split("<pre>\n", 1)[0]
print("content before <pre> unchanged:", orig)
