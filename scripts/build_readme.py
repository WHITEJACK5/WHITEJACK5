"""Build README.md from a template plus a verbatim art file.

The art is inserted by reading the source file as UTF-8 and writing the
characters through untouched. Nothing re-types or re-encodes the braille, so
what lands in the README is byte-identical to the source.
"""

import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ART_SRC = pathlib.Path(r"C:\Users\BHARADWAJA REDDY\Downloads\art.txt")
README = ROOT / "README.md"
ART_OUT = ROOT / "assets" / "banner.txt"

# strip anything after the braille on each line (e.g. a trailing note)
clean = []
for line in ART_SRC.read_text(encoding="utf-8").splitlines():
    buf = []
    for ch in line:
        if 0x2800 <= ord(ch) <= 0x28FF or ord(ch) == 32:
            buf.append(ch)
        else:
            break
    clean.append("".join(buf))
while clean and not clean[-1].strip():
    clean.pop()

widths = sorted({len(l) for l in clean})
nonbraille = {c for c in "".join(clean) if not (0x2800 <= ord(c) <= 0x28FF or ord(c) == 32)}
print(f"art: {len(clean)} lines, widths={widths}, non-braille={nonbraille or 'none'}")
assert not nonbraille, f"art still contains {nonbraille}"

ART_OUT.parent.mkdir(exist_ok=True)
ART_OUT.write_text("\n".join(clean) + "\n", encoding="utf-8")
print(f"wrote {ART_OUT} ({ART_OUT.stat().st_size} bytes)")

art_block = "\n".join(clean)

BODY = f"""<div align="center">

<pre>
{art_block}
</pre>

</div>

---

<samp>GitHub</samp> `@WHITEJACK5` &nbsp;&middot;&nbsp;
<samp>LinkedIn</samp> `/in/devireddybharadwaja` &nbsp;&middot;&nbsp;
<samp>Focus</samp> `Applied AI / Full-Stack` &nbsp;&middot;&nbsp;
<samp>Building</samp> `in public`

---

Applied AI engineer and full-stack builder. I turn messy data and product
ideas into systems that are measurable and explainable &mdash; fraud risk
engines, calibrated models, and the interfaces that make them usable.

I care about the parts that are easy to skip: reproducible evaluation, honest
model limits, and documentation that matches what the code actually does.

---

## What I Build

- **Risk intelligence** &mdash; real-time fraud detection, mule-ring graph
  analysis, calibrated decision policy
- **Explainable ML** &mdash; SHAP attribution, model cards, limitations stated
  next to the claims
- **ML systems** &mdash; leakage-aware validation, temporal splits, drift
  monitoring, reproducible pipelines
- **Backend** &mdash; typed REST APIs, idempotency, rate limiting, audit trails
- **Product** &mdash; Next.js interfaces, dashboards, Docker delivery

---

## Toolkit

**Languages** `Python` `JavaScript` `TypeScript` `Java` `SQL` `Bash`

**AI / ML** `XGBoost` `LightGBM` `SHAP` `scikit-learn` `MLflow` `NetworkX`

**Backend** `FastAPI` `Flask` `Node.js` `Express` `REST` `WebSocket`

**Frontend** `Next.js` `React` `Tailwind` `ReactFlow` `Mermaid` `Monaco`

**Data** `PostgreSQL` `MongoDB` `SQLite` `Prisma`

**Platform** `Docker` `GitHub Actions` `Turborepo` `pytest` `Vitest`

---

## Selected Work

### TRACER &mdash; Real-Time Mule-Ring Defense

Defense-only risk engine scoring transactions in under 50&nbsp;ms. Graph
topology catches what a row-wise model misses: devices fanning out across
payment identities, and same-amount repeat smurfing. A bounded agent can only
approve, challenge, or hold &mdash; and every action lands in a hash-chained
audit ledger.

`samp` Python &middot; FastAPI &middot; Next.js &middot; XGBoost &middot; SHAP &middot; NetworkX

[View repository](https://github.com/WHITEJACK5/TRACER-Real-Time-Mule-Ring-Defense)

### loan-default-risk

Probability-of-default modeling with the leakage audit written down: 151 raw
columns reduced to 24 origination-time columns, and a temporal split instead of
a random one. Calibration and a profit-aware policy turn the score into an
approve/reject decision, and SHAP explains it.

`samp` Python &middot; LightGBM &middot; MLflow &middot; SHAP &middot; FastAPI &middot; Docker

[View repository](https://github.com/WHITEJACK5/loan-default-risk) &middot;
[Demo](https://whitejack5-loan-default-risk.hf.space)

### white-collars

Full-stack job portal that scrapes company career pages and lets applicants
apply in one click with saved documents. Deliberately staged &mdash; monolith,
then feature-based decomposition, then a Turborepo monorepo with OpenAPI
contracts &mdash; with the honest stopping point documented rather than faked.

`samp` Node.js &middot; Express &middot; MongoDB &middot; EJS &middot; Turborepo &middot; Docker

[View repository](https://github.com/WHITEJACK5/white-collars)

### DYNAMIC-QR

Local-first QR generator: 25+ payload types, static and dynamic codes, live
preview, password and expiry protection, and scan analytics on a local SQLite
database that initialises itself on first run.

`samp` Python &middot; Flask &middot; SQLite &middot; JWT

[View repository](https://github.com/WHITEJACK5/DYNAMIC-QR)

---

## Approach

- **Reproducible evaluation before optimization.** A number you cannot
  re-derive is not a result.
- **Explainability is part of the model, not a wrapper.** If nobody can say why
  a transaction was held, the score is not usable.
- **Document the limits.** A prototype that admits its own failure modes is
  more useful than one that overstates its accuracy.
- **Small, testable slices.** A change that can be reviewed is a change that
  can be trusted.

---

## Connect

- **GitHub** &mdash; [github.com/WHITEJACK5](https://github.com/WHITEJACK5)
- **LinkedIn** &mdash; [linkedin.com/in/devireddybharadwaja](https://www.linkedin.com/in/devireddybharadwaja)
"""

README.write_text(BODY, encoding="utf-8")
print(f"wrote {README} ({README.stat().st_size} bytes)")

# verify the art survived the round trip byte-for-byte
back = README.read_text(encoding="utf-8")
assert art_block in back, "art block missing from README"
rebuilt = back.split("<pre>\n", 1)[1].split("\n</pre>", 1)[0]
print(f"round-trip ok: {rebuilt == art_block}")
