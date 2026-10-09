"""Rebuild README.md with the Creation of Adam dither animation as the header.

The braille banner that used to sit here has been replaced by
assets/creation-of-adam.gif, rendered by the recipe below. Everything else is
plain text written directly.
"""

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
HERO = ROOT / "assets" / "creation-of-adam.gif"

if not HERO.exists():
    raise SystemExit(f"missing {HERO} - render it before rebuilding the README")

body = f"""<div align="center">

<img src="./assets/creation-of-adam.gif" width="600"
     alt="Dithered animation of Michelangelo's Creation of Adam, rendered from this repository" />

<br/>

<samp>GitHub</samp> `@WHITEJACK5` &nbsp;&middot;&nbsp;
<samp>LinkedIn</samp> `/in/devireddybharadwaja` &nbsp;&middot;&nbsp;
<samp>Focus</samp> `Applied AI / Full-Stack`

<br/><br/>

<a href="https://github.com/WHITEJACK5"><img src="https://img.shields.io/badge/GitHub-WHITEJACK5-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub" /></a>
<a href="https://www.linkedin.com/in/devireddybharadwaja"><img src="https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn" /></a>
<a href="mailto:poison.white12@gmail.com"><img src="https://img.shields.io/badge/Email-poison.white12@gmail.com-EA4335?style=for-the-badge&logo=gmail&logoColor=white" alt="Email" /></a>
<a href="https://www.instagram.com/futurebug5"><img src="https://img.shields.io/badge/Instagram-@futurebug5-E4405F?style=for-the-badge&logo=instagram&logoColor=white" alt="Instagram" /></a>

</div>

---

<img src="./hd/whoami.svg" width="900" alt="whoami" />

Applied AI engineer and full-stack builder. I turn messy data and product ideas
into systems that are measurable and explainable &mdash; fraud risk engines,
calibrated models, and the interfaces that make them usable.

I care about the parts that are easy to skip: reproducible evaluation, honest
model limits, and documentation that matches what the code actually does.

---

## \U0001F4BB Tech Stack

**Languages** &mdash; taken from the GitHub language breakdown across the public
repositories, not from a wishlist.

<p>
<img src="https://img.shields.io/badge/Python-42.6%25-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 42.6%" />
<img src="https://img.shields.io/badge/Jupyter%20Notebook-29.7%25-DA5B0B?style=flat-square&logo=jupyter&logoColor=white" alt="Jupyter Notebook 29.7%" />
<img src="https://img.shields.io/badge/JavaScript-11.1%25-F7DF1E?style=flat-square&logo=javascript&logoColor=black" alt="JavaScript 11.1%" />
<img src="https://img.shields.io/badge/TypeScript-9.2%25-3178C6?style=flat-square&logo=typescript&logoColor=white" alt="TypeScript 9.2%" />
<img src="https://img.shields.io/badge/HTML-2.8%25-E34F26?style=flat-square&logo=html5&logoColor=white" alt="HTML 2.8%" />
<img src="https://img.shields.io/badge/EJS-2.4%25-B4CA65?style=flat-square&logo=ejs&logoColor=black" alt="EJS 2.4%" />
<img src="https://img.shields.io/badge/CSS-1.8%25-1572B6?style=flat-square&logo=css3&logoColor=white" alt="CSS 1.8%" />
<img src="https://img.shields.io/badge/Dockerfile-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Dockerfile" />
</p>

**AI / ML** &mdash; used in the fraud and credit-risk work

<p>
<img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python" />
<img src="https://img.shields.io/badge/XGBoost-FF9900?style=flat-square&logoColor=black" alt="XGBoost" />
<img src="https://img.shields.io/badge/LightGBM-8CAA55?style=flat-square&logoColor=white" alt="LightGBM" />
<img src="https://img.shields.io/badge/scikit--learn-F7931E?style=flat-square&logo=scikit-learn&logoColor=white" alt="scikit-learn" />
<img src="https://img.shields.io/badge/SHAP-00C2FF?style=flat-square&logoColor=black" alt="SHAP" />
<img src="https://img.shields.io/badge/MLflow-0194E2?style=flat-square&logo=mlflow&logoColor=white" alt="MLflow" />
<img src="https://img.shields.io/badge/NetworkX-0055A4?style=flat-square&logoColor=white" alt="NetworkX" />
</p>

**Backend**

<p>
<img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI" />
<img src="https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white" alt="Flask" />
<img src="https://img.shields.io/badge/Node.js-339933?style=flat-square&logo=nodedotjs&logoColor=white" alt="Node.js" />
<img src="https://img.shields.io/badge/Express-404D59?style=flat-square&logo=express&logoColor=white" alt="Express" />
<img src="https://img.shields.io/badge/REST-6BA539?style=flat-square&logoColor=white" alt="REST" />
</p>

**Frontend**

<p>
<img src="https://img.shields.io/badge/Next.js-000000?style=flat-square&logo=nextdotjs&logoColor=white" alt="Next.js" />
<img src="https://img.shields.io/badge/React-20232A?style=flat-square&logo=react&logoColor=61DAFB" alt="React" />
<img src="https://img.shields.io/badge/Tailwind%20CSS-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white" alt="Tailwind CSS" />
<img src="https://img.shields.io/badge/ReactFlow-FF7A00?style=flat-square&logoColor=white" alt="ReactFlow" />
<img src="https://img.shields.io/badge/Mermaid-8A7DB1?style=flat-square&logoColor=white" alt="Mermaid" />
<img src="https://img.shields.io/badge/Monaco%20Editor-4FC3F7?style=flat-square&logoColor=black" alt="Monaco Editor" />
</p>

**Data &amp; Platform**

<p>
<img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL" />
<img src="https://img.shields.io/badge/MongoDB-47A248?style=flat-square&logo=mongodb&logoColor=white" alt="MongoDB" />
<img src="https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white" alt="SQLite" />
<img src="https://img.shields.io/badge/Prisma-2D3748?style=flat-square&logo=prisma&logoColor=white" alt="Prisma" />
<img src="https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker" />
<img src="https://img.shields.io/badge/GitHub%20Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white" alt="GitHub Actions" />
<img src="https://img.shields.io/badge/Turborepo-EF4A8B?style=flat-square&logo=turborepo&logoColor=white" alt="Turborepo" />
<img src="https://img.shields.io/badge/pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white" alt="pytest" />
</p>

---

<img src="./hd/projects.svg" width="900" alt="projects" />

<details open>
<summary><b>&#9654; TRACER &mdash; Real-Time Mule-Ring Defense</b></summary>

<br/>

Defense-only risk engine scoring Razorpay transactions in under 50&nbsp;ms.
Graph topology catches what a row-wise model misses: devices fanning out across
payment identities, and same-amount repeat smurfing. A bounded agent can only
approve, challenge, or hold &mdash; and every action lands in a hash-chained
audit ledger.

<samp>Stack</samp> Python &middot; FastAPI &middot; Next.js &middot; XGBoost &middot; SHAP &middot; NetworkX
<br/>
<a href="https://github.com/WHITEJACK5/TRACER-Real-Time-Mule-Ring-Defense">Repository</a>

</details>

<details>
<summary><b>&#9654; loan-default-risk</b></summary>

<br/>

Probability-of-default modeling on LendingClub, with the leakage audit written
down: 151 raw columns reduced to 24 origination-time columns, and a temporal
split instead of a random one. Calibration and a profit-aware policy turn the
score into an approve/reject decision, and SHAP explains it.

<samp>Stack</samp> Python &middot; LightGBM &middot; MLflow &middot; SHAP &middot; FastAPI &middot; Docker
<br/>
<a href="https://github.com/WHITEJACK5/loan-default-risk">Repository</a> &middot; <a href="https://whitejack5-loan-default-risk.hf.space">Demo</a>

</details>

<details>
<summary><b>&#9654; white-collars</b></summary>

<br/>

Full-stack job portal that scrapes company career pages and lets applicants
apply in one click with saved documents. Deliberately staged &mdash; monolith,
then feature-based decomposition, then a Turborepo monorepo with OpenAPI
contracts &mdash; with the honest stopping point documented rather than faked.

<samp>Stack</samp> Node.js &middot; Express &middot; MongoDB &middot; EJS &middot; Turborepo &middot; Docker
<br/>
<a href="https://github.com/WHITEJACK5/white-collars">Repository</a>

</details>

<details>
<summary><b>&#9654; DYNAMIC-QR</b></summary>

<br/>

Local-first QR generator: 25+ payload types, static and dynamic codes, live
preview, password and expiry protection, and scan analytics on a local SQLite
database that initialises itself on first run.

<samp>Stack</samp> Python &middot; Flask &middot; SQLite &middot; JWT
<br/>
<a href="https://github.com/WHITEJACK5/DYNAMIC-QR">Repository</a>

</details>

---

<img src="./hd/expertise.svg" width="900" alt="expertise" />

| Domain | What I actually do |
| :-- | :-- |
| **Risk intelligence** | Mule-ring graph detection, calibrated risk scoring, threshold policy |
| **Explainable ML** | SHAP attribution, model cards, limitations stated next to the claims |
| **ML systems** | Leakage-aware validation, temporal splits, drift monitoring, reproducible pipelines |
| **Backend** | Typed REST APIs, idempotency, rate limiting, audit trails |
| **Product** | Next.js interfaces, dashboards, Docker delivery, CI that gates merges |

---

<img src="./hd/approach.svg" width="900" alt="approach" />

- **Reproducible evaluation before optimization.** A number you cannot re-derive
  is not a result.
- **Explainability is part of the model, not a wrapper.** If nobody can say why
  a transaction was held, the score is not usable.
- **Document the limits.** A prototype that admits its own failure modes is
  more useful than one that overstates its accuracy.
- **Small, testable slices.** A change that can be reviewed is a change that
  can be trusted.

---

## \U0001F4CA GitHub Stats

Every graphic below is generated inside this repository by a scheduled action,
from the GitHub GraphQL API. No third-party widget service is involved, so
nothing here can rate-limit or go dark.

<img src="./stats.svg" width="520" alt="Contribution totals and weekly trend" />

<br/>

<img src="./streak.svg" width="520" alt="Contribution streak" />

<br/>

<img src="./langs.svg" width="520" alt="Top languages by bytes and by repository" />

<br/>

<img src="./year.svg" width="520" alt="Contribution calendar, one character per day" />

<br/>

<sub>Refreshed nightly by <code>.github/workflows/refresh-stats.yml</code>, pinned to whole
UTC days so the output is byte-stable between runs, and filtered to public
repositories so the numbers match what a visitor sees. Columns, not lines: a day
with no contributions is empty space, not a point on a curve between
neighbours.</sub>

---

<img src="./hd/connect.svg" width="900" alt="connect" />

<div align="center">

<a href="https://github.com/WHITEJACK5"><samp>github.com/WHITEJACK5</samp></a>
&nbsp;&nbsp;&middot;&nbsp;&nbsp;
<a href="https://www.linkedin.com/in/devireddybharadwaja"><samp>linkedin.com/in/devireddybharadwaja</samp></a>
&nbsp;&nbsp;&middot;&nbsp;&nbsp;
<a href="mailto:poison.white12@gmail.com"><samp>poison.white12@gmail.com</samp></a>

<br/><br/>

<samp>WHITEJACK5 -- DEVIREDDY BHARADWAJA REDDY</samp>

</div>
"""

README.write_text(body, encoding="utf-8")
print(f"wrote {README} ({README.stat().st_size:,} bytes)")

back = README.read_text(encoding="utf-8")
missing = [r for r in sorted(set(re.findall(r'src="\./([^"]+)"', back)))
           if not (ROOT / r).exists()]
print("hero referenced:", "./assets/creation-of-adam.gif" in back)
print("braille block gone:", "<pre>" not in back)
print("missing local image files:", missing or "none")
