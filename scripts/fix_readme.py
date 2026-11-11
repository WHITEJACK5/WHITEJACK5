"""Rebuild README.md with targeted, resume-synced content.

Edits the generator (not README.md) so changes survive regeneration.
Preserves any content between <!-- REPOS:START --> and <!-- REPOS:END -->.
"""

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
HERO = ROOT / "assets" / "creation-of-adam.gif"

if not HERO.exists():
    raise SystemExit(f"missing {HERO} - render it before rebuilding the README")

existing = README.read_text(encoding="utf-8") if README.exists() else ""
m = re.search(r"<!-- REPOS:START -->(.*?)<!-- REPOS:END -->", existing, re.S)
repos_inner = m.group(1) if m else "\n"

body = f"""<div align="center">

<img src="./assets/creation-of-adam.gif" width="900"
     alt="Dithered animation of Michelangelo's Creation of Adam, rendered from this repository" />

<br/>

**Devireddy Bharadwaja Reddy**

<samp>GitHub</samp> `@WHITEJACK5` &nbsp;&middot;&nbsp;
<samp>LinkedIn</samp> `/in/devireddybharadwaja` &nbsp;&middot;&nbsp;
<samp>Focus</samp> `Applied AI / Full-Stack`

<samp>B.Tech Computer Engineering (AI &amp; ML), Ramrao Adik Institute of Technology (RAIT), Navi Mumbai, 2024&ndash;2028, GPA 8.8/10</samp>

<br/><br/>

<a href="https://github.com/WHITEJACK5"><img src="https://img.shields.io/badge/GitHub-WHITEJACK5-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub" /></a>
<a href="https://www.linkedin.com/in/devireddybharadwaja"><img src="https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn" /></a>
<a href="https://leetcode.com/u/devireddy5"><img src="https://img.shields.io/badge/LeetCode-devireddy5-FFA116?style=for-the-badge&logo=leetcode&logoColor=black" alt="LeetCode" /></a>
<a href="mailto:bharadwajareddydevireddy@gmail.com"><img src="https://img.shields.io/badge/Email-bharadwajareddydevireddy%40gmail.com-EA4335?style=for-the-badge&logo=gmail&logoColor=white" alt="Email" /></a>
<a href="https://www.instagram.com/futurebug5"><img src="https://img.shields.io/badge/Instagram-@futurebug5-E4405F?style=for-the-badge&logo=instagram&logoColor=white" alt="Instagram" /></a>

</div>

---

<img src="./hd/whoami.svg" width="900" alt="whoami" />

Applied AI engineer and full-stack builder. I turn messy data and product ideas
into systems that are measurable and explainable &mdash; fraud risk engines,
calibrated models, and the interfaces that make them usable.

I care about the parts that are easy to skip: reproducible evaluation, honest
model limits, and documentation that matches what the code actually does.

Based in Navi Mumbai, India. Open to Applied ML / Full-Stack roles and internships.

---

## Tech Stack

**Languages**  
![Python](https://img.shields.io/badge/Python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![SQL](https://img.shields.io/badge/SQL-4479A1?style=for-the-badge&logo=postgresql&logoColor=white) ![Java](https://img.shields.io/badge/Java-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white) ![C](https://img.shields.io/badge/C-00599C?style=for-the-badge&logo=c&logoColor=white) ![C++](https://img.shields.io/badge/C%2B%2B-00599C?style=for-the-badge&logo=c%2B%2B&logoColor=white)

**ML**  
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white) ![XGBoost](https://img.shields.io/badge/XGBoost-337AB7?style=for-the-badge&logo=xgboost&logoColor=white) ![LightGBM](https://img.shields.io/badge/LightGBM-02569B?style=for-the-badge&logo=lightgbm&logoColor=white) ![SHAP](https://img.shields.io/badge/SHAP-BE123C?style=for-the-badge&logoColor=white) ![MLflow](https://img.shields.io/badge/MLflow-0194E2?style=for-the-badge&logo=mlflow&logoColor=white) ![Evidently](https://img.shields.io/badge/Evidently-6C47FF?style=for-the-badge&logoColor=white)

**Backend**  
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white) ![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white) ![Node.js](https://img.shields.io/badge/Node.js-339933?style=for-the-badge&logo=nodedotjs&logoColor=white) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white) ![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white)

**Frontend**  
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB) ![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white) ![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)

**DevOps**  
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white) ![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white) ![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white) ![pytest](https://img.shields.io/badge/pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white) ![Playwright](https://img.shields.io/badge/Playwright-2EAD33?style=for-the-badge&logo=playwright&logoColor=white)

---


<img src="./hd/projects.svg" width="900" alt="projects" />

<details open>
<summary><b>&#9654; TRACER &mdash; Real-Time Mule-Ring Defense</b></summary>

<br/>

Defense-only risk engine scoring Razorpay transactions, p50 53 ms at 18 req/s.
Graph topology catches what a row-wise model misses: devices fanning out across
payment identities, and same-amount repeat smurfing. A bounded agent can only
approve, challenge, or hold &mdash; and every action lands in a hash-chained
audit ledger.

<samp>Stack</samp> Python &middot; FastAPI &middot; Next.js &middot; XGBoost &middot; SHAP &middot; NetworkX
<br/>
<samp>Result</samp> NetworkX, XGBoost, SHAP, FastAPI, Next.js, Docker. Fan-out &gt;= 4 and same-amount smurfing detection; p50 53 ms at 18 req/s; 83% of Bayes-ceiling AUPRC on a synthetic benchmark; 156 pytest, 6 Playwright E2E.
<br/>
<a href="https://github.com/WHITEJACK5/TRACER-Real-Time-Mule-Ring-Defense">Repository</a>

</details>

<details>
<summary><b>&#9654; loan-default-risk</b></summary>

<br/>

Probability-of-default modeling on 1.35M LendingClub loans, with the leakage audit written
down: 151 raw columns reduced to 24 origination-time columns, and a temporal
split instead of a random one. Calibration and a profit-aware policy turn the
score into an approve/reject decision, and SHAP explains it.

<samp>Stack</samp> Python &middot; LightGBM &middot; MLflow &middot; SHAP &middot; FastAPI &middot; Docker
<br/>
<samp>Result</samp> LightGBM, FastAPI, Docker, MLflow, SHAP. Leakage-audited PD on 1.35M LendingClub loans; ROC-AUC 0.69, PR-AUC 0.35 on a 2017+ hold-out. API p50 29 ms, PSI drift checks, +$7.4M simulated profit policy, 85 tests.
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

### Latest repositories
<!-- REPOS:START -->{repos_inner}<!-- REPOS:END -->

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

## Education &amp; Achievements

- **B.Tech Computer Engineering (AI &amp; ML)**, Ramrao Adik Institute of Technology (RAIT), Navi Mumbai, 2024&ndash;2028, GPA 8.8/10
- **4th Place, Arohan 2.0 National-Level Hackathon (2025)**
- **Coursework:** Machine Learning, Deep Learning, DSA, DBMS, OS, Computer Networks

## Certifications

- Machine Learning Specialization, Stanford Online &amp; DeepLearning.AI (Jul 2026)
- Generative AI with Large Language Models, DeepLearning.AI &amp; AWS (Aug 2026)
- Retrieval-Augmented Generation, DeepLearning.AI (Aug 2026)

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

## GitHub Stats

<img src="./stats.svg" width="520" alt="Contributions in the last year, active days and weekly trend" />

<img src="./streak.svg" width="520" alt="Current and longest contribution streak" />

<img src="./langs.svg" width="520" alt="Top languages by bytes and by repository" />

<img src="./year.svg" width="520" alt="Contribution calendar, one character per day" />

---

### Random Dev Quote

![](https://quotes-github-readme.vercel.app/api?type=horizontal&theme=dark)

---


<img src="./hd/connect.svg" width="900" alt="connect" />

<div align="center">

<a href="https://github.com/WHITEJACK5"><samp>github.com/WHITEJACK5</samp></a>
&nbsp;&nbsp;&middot;&nbsp;&nbsp;
<a href="https://www.linkedin.com/in/devireddybharadwaja"><samp>linkedin.com/in/devireddybharadwaja</samp></a>
&nbsp;&nbsp;&middot;&nbsp;&nbsp;
<a href="mailto:bharadwajareddydevireddy@gmail.com"><samp>bharadwajareddydevireddy@gmail.com</samp></a>

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
print("repos markers:", "<!-- REPOS:START -->" in back and "<!-- REPOS:END -->" in back)
