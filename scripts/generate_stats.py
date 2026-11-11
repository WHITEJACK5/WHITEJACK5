"""Generate the profile README's data graphics as static SVG.

No third-party widget service is involved: this script is the whole data
source. Standard library only (urllib), so there is nothing to break in CI.

Two determinism traps the guide calls out, both handled here:

1. contributionsCollection is pinned to whole UTC days. Left alone it measures
   "the past year" from the moment of the request, so two runs minutes apart
   bucket days into different weeks and the output shifts every run.
2. Repositories are filtered to privacy: PUBLIC. A personal token sees private
   repos and the workflow's does not, so without the filter the numbers depend
   on who ran the script.
"""

import base64
import datetime as dt
import json
import os
import pathlib
import subprocess
import sys
import textwrap
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONTS = ROOT / "fonts"
API = "https://api.github.com/graphql"

RAMP = " .`" + chr(58) + "-=+*cs#%@"
INK = "#39FF14"
DIM = "#8AFF57"
FAINT = "#1A2B1A"
BG = "#0A0F08"


def token() -> str:
    t = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not t:
        sys.exit("GITHUB_TOKEN is required")
    return t.strip()


def login() -> str:
    return os.environ.get("GH_LOGIN", "WHITEJACK5").strip()


def gql(query: str, variables: dict) -> dict:
    req = urllib.request.Request(
        API,
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={
            "Authorization": f"Bearer {token()}",
            "User-Agent": "profile-readme-stats",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        body = json.load(r)
    if body.get("errors"):
        raise SystemExit(f"GraphQL error: {body['errors']}")
    return body["data"]


def utc_window():
    """Pin to whole UTC days - determinism trap 1."""
    now = dt.datetime.now(dt.timezone.utc)
    to = now.replace(hour=23, minute=59, second=59, microsecond=0)
    frm = (now - dt.timedelta(days=364)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    return frm, to


def face(w: str) -> str:
    b64 = base64.b64encode((FONTS / w).read_bytes()).decode("ascii")
    return "data:font/woff2;base64," + b64


def svg_open(w: int, h: int, title: str, weights=("basic-regular",)) -> str:
    faces = "\n".join(
        f"@font-face{{font-family:'JBMono';src:url({face(n + '.woff2')}) "
        f"format('woff2');font-weight:{'700' if 'bold' in n else '400'};"
        "font-style:normal;font-display:swap}"
        for n in weights
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}">'
        f"<style>{faces}"
        f"text{{font-family:'JBMono',monospace;fill:{INK}}}"
        f".d{{fill:{DIM}}}.f{{fill:{FAINT}}}"
        f"</style>"
        f'<rect width="{w}" height="{h}" fill="{BG}"/>'
    )


def esc(s) -> str:
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def t(x, y, s, size=13, cls="", weight=400, anchor="start") -> str:
    c = f' class="{cls}"' if cls else ""
    w = f' font-weight="{weight}"' if weight != 400 else ""
    return (
        f'<text x="{x}" y="{y}" font-size="{size}"{c}{w} '
        f'text-anchor="{anchor}">{esc(s)}</text>'
    )


def write(name: str, body: str) -> None:
    p = ROOT / name
    p.write_text(body, encoding="utf-8")
    print(f"{name:14} {p.stat().st_size:>7,} bytes")


def fmt(n) -> str:
    """Compact enough that a 26px number never outgrows its tile."""
    n = int(n)
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 100_000:
        return f"{n / 1000:.0f}k"
    return f"{n:,}"


# ---------------------------------------------------------------- hero + spark


def hero(days, totals) -> str:
    """Total contributions + weekly sparkline.

    A weekly aggregate is where a line/area is defensible: daily counts are
    sparse and discrete, so a line through 0,0,11,0 would claim values that
    never existed.
    """
    w, h = 520, 170
    s = svg_open(w, h, "Contribution totals and weekly trend", ("basic-regular", "basic-bold"))
    s += t(20, 42, f"{totals['total']:,}", 34, weight=700)
    s += t(20, 64, "contributions in the last year", 12, cls="d")
    s += t(20, 86, f"{totals['active_days']} active days", 12, cls="d")

    weeks = totals["weeks"]
    x0, y0, ww, hh = 20, 104, w - 40, 34
    top = max(weeks) or 1
    bw = ww / len(weeks)
    for i, v in enumerate(weeks):
        bh = (v / top) * hh
        s += (
            f'<rect x="{x0 + i * bw:.2f}" y="{y0 + hh - bh:.2f}" '
            f'width="{max(1.0, bw - 1.5):.2f}" height="{bh:.2f}" fill="{DIM}"/>'
        )
    # label below the baseline so it cannot collide with the bars
    s += t(x0, y0 + hh + 18, f"weekly peak {top}", 10, cls="d")
    s += "</svg>"
    return s


# ---------------------------------------------------------------- streak


def streak(days) -> str:
    w, h = 520, 150
    s = svg_open(w, h, "Contribution streak", ("basic-regular", "basic-bold"))
    s += t(20, 40, str(streak_stats["current"]), 30, weight=700)
    s += t(20, 60, "current streak (days)", 12, cls="d")
    s += t(280, 40, str(streak_stats["longest"]), 30, weight=700)
    s += t(280, 60, "longest streak (days)", 12, cls="d")

    s += t(20, 96, f"current since {streak_stats['current_from'] or '-'}", 11, cls="d")
    s += t(280, 96, f"longest {streak_stats['longest_from'] or '-'} to {streak_stats['longest_to'] or '-'}", 11, cls="d")

    # last 28 days as cells - columns, not a line: a zero day is empty space
    recent = days[-28:]
    cell, gap = 14, 3
    x0 = 20
    y0 = 112
    for i, d in enumerate(recent):
        v = d["count"]
        idx = 0 if v == 0 else min(len(RAMP) - 1, 1 + int(v / 4 * (len(RAMP) - 2)))
        ch = RAMP[idx]
        col = INK if v else FAINT
        s += t(x0 + i * (cell + gap), y0 + 12, ch, 12, weight=700).replace(
            f'fill:{INK}', f'fill:{col}'
        )
    s += t(20, h - 8, "last 28 days", 10, cls="d")
    s += "</svg>"
    return s


# ---------------------------------------------------------------- languages


def langs(user) -> str:
    # `User.languages` does not exist in the schema - languages hang off each
    # repository, so aggregate across the PUBLIC, non-fork repos. Summing edges
    # (rather than taking each repo's top language) matches what GitHub's own
    # language bar counts.
    by_size: dict[str, int] = {}
    repo_counts: dict[str, int] = {}
    for r in user["repositories"]["nodes"]:
        for e in r["languages"]["edges"]:
            name = e["node"]["name"]
            by_size[name] = by_size.get(name, 0) + e["size"]
        if r["primaryLanguage"]:
            n = r["primaryLanguage"]["name"]
            repo_counts[n] = repo_counts.get(n, 0) + 1

    size_edges = sorted(
        ({"size": v, "node": {"name": k}} for k, v in by_size.items()),
        key=lambda e: e["size"],
        reverse=True,
    )
    total = sum(e["size"] for e in size_edges) or 1

    w, h = 520, 200
    s = svg_open(w, h, "Top languages by bytes and by repository",
                 ("basic-regular", "basic-bold"))
    s += t(20, 32, "languages by bytes", 13, weight=700)
    bar_x, bar_y, bar_w = 20, 44, w - 40
    x = bar_x
    for e in size_edges[:6]:
        seg = (e["size"] / total) * bar_w
        s += (
            f'<rect x="{x:.2f}" y="{bar_y}" width="{max(1.0, seg - 1):.2f}" '
            f'height="14" fill="{DIM}"/>'
        )
        x += seg
    y = bar_y + 34
    for e in size_edges[:6]:
        pct = e["size"] / total * 100
        s += t(20, y, e["node"]["name"], 12)
        s += t(w - 20, y, f"{pct:.1f}%", 12, cls="d", anchor="end")
        y += 20

    # by repo, from the same payload - the PUBLIC filter above is what makes
    # these counts agree with the workflow's numbers
    top = sorted(repo_counts.items(), key=lambda kv: kv[1], reverse=True)[:6]
    rtotal = sum(repo_counts.values()) or 1

    s += t(20, y + 16, "primary language by repository", 13, weight=700)
    y += 38
    for name, n in top:
        s += t(20, y, name, 12)
        s += t(w - 20, y, f"{n}/{rtotal}", 12, cls="d", anchor="end")
        y += 18
    s += "</svg>"
    return s


# ---------------------------------------------------------------- the year


def year_svg(days) -> str:
    """One character per day, using the portrait's own ramp.

    Honest by construction: every day is a cell, so a zero day is visibly empty.
    Emitted as one <text> per weekday row using <tspan> per cell - 7 text
    nodes instead of 365, which is both smaller and much faster to render.
    """
    weeks = 53
    cw, ch = 9, 11
    pad = 20
    w = pad * 2 + weeks * cw
    h = pad * 2 + 7 * ch
    s = svg_open(w, h, "Contribution calendar, one character per day",
                 ("basic-regular", "basic-bold"))

    counts = [d["count"] for d in days]
    top = max(counts) or 1
    top_idx = len(RAMP) - 1

    weeks = 53
    cw, ch = 9, 11
    pad = 20
    w = pad * 2 + weeks * cw
    h = pad * 2 + 7 * ch
    s = svg_open(w, h, "Contribution calendar, one character per day",
                 ("basic-regular", "basic-bold"))

    counts = [d["count"] for d in days]
    top = max(counts) or 1
    top_idx = len(RAMP) - 1

    dows = ["Mon", "", "Wed", "", "Fri", "", "Sun"]
    for r, label in enumerate(dows):
        if label:
            s += t(pad - 6, pad + r * ch + 8, label, 9, cls="d", anchor="end")

    # Anchor the grid to the real calendar: row = weekday (Mon=0), column =
    # week number. Deriving the offset from the first day's weekday is what
    # keeps the month labels honest - assuming 7 cells per column from index 0
    # silently shifts every month by a few days.
    first = dt.date.fromisoformat(days[0]["date"])
    offset = first.weekday()  # Monday=0

    cells = [[] for _ in range(7)]
    month_marks = []  # (column, label) for the first day of each month
    prev_month = None
    prev_year = None

    for i, d in enumerate(days):
        date = dt.date.fromisoformat(days[i]["date"])
        if date.month != prev_month or date.year != prev_year:
            month_marks.append(((i + offset) // 7, date.strftime("%b")))
            prev_month, prev_year = date.month, date.year

        col = (i + offset) // 7
        row = (i + offset) % 7
        v = d["count"]
        if v == 0:
            ch_ = " "
            colr = FAINT
        else:
            # sqrt keeps a single contribution visible without flattening the top
            frac = (v / top) ** 0.5
            idx = max(2, min(top_idx, int(frac * top_idx)))
            ch_ = RAMP[idx]
            colr = INK if v >= top * 0.5 else DIM
        cells[row].append((col, ch_, colr))

    for row in range(7):
        if not cells[row]:
            continue
        y = pad + row * ch + 8
        # per-cell colour needs a tspan each, but one shared <text> per row
        spans = []
        for col, ch_, colr in cells[row]:
            spans.append(
                f'<tspan x="{pad + col * cw}" fill="{colr}">{esc(ch_)}</tspan>'
            )
        s += (
            f'<text y="{y}" font-size="10" font-weight="700" '
            f'xml:space="preserve">{"".join(spans)}</text>'
        )

    # One label per month at the column where it actually starts. A 365-day
    # window can straddle a year boundary (Sep -> Sep), which legitimately puts
    # the same month name twice; disambiguate the later one with its year
    # instead of hiding it.
    last_x = -99
    for col, label in month_marks:
        x = pad + col * cw
        if col >= weeks or x <= last_x + 18:  # 18px ~= 3 chars at 9px
            continue
        s += t(x, pad - 6, label, 9, cls="d")
        last_x = x
    s += t(w - 20, pad - 6, str(dt.date.fromisoformat(days[-1]["date"]).year),
           9, cls="d", anchor="end")
    s += "</svg>"
    return s


# ---------------------------------------------------------------- new cards


def grad_defs() -> str:
    return (
        '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{INK}"/>'
        f'<stop offset="1" stop-color="{DIM}"/>'
        "</linearGradient></defs>"
    )


def profile_card(m: dict) -> str:
    """3x3 all-time tiles: first row gradient, the rest white for contrast."""
    w, h = 520, 210
    s = svg_open(w, h, "All-time GitHub activity",
                 ("basic-regular", "basic-bold")) + grad_defs()
    tiles = [
        ("commits", m["commits"]),
        ("pull requests", m["prs"]),
        ("issues opened", m["issues"]),
        ("reviews", m["reviews"]),
        ("stars earned", m["stars"]),
        ("public repos", m["public_repos"]),
        ("followers", m["followers"]),
        ("private contributions", m["private"]),
        ("years on GitHub", m["years"]),
    ]
    xs, ys = (20, 180, 340), (58, 116, 174)
    for i, (label, value) in enumerate(tiles):
        x, y = xs[i % 3], ys[i // 3]
        fill = ' fill="url(#g)"' if i < 3 else ""
        s += (f'<text x="{x}" y="{y}" font-size="26" font-weight="700"{fill}>'
              f'{esc(fmt(value))}</text>')
        s += t(x, y + 19, label, 10, cls="d")
    s += "</svg>"
    return s


def yearly_card(per_year) -> str:
    """Contributions per calendar year, last six at most."""
    rows = per_year[-6:]
    w, h = 520, 190
    s = svg_open(w, h, "Contributions per calendar year",
                 ("basic-regular", "basic-bold")) + grad_defs()
    s += t(20, 30, "contributions per year", 13, weight=700)

    x0, x1 = 20, w - 20
    base = 134
    slot = (x1 - x0) / max(1, len(rows))
    bar_w = min(44.0, slot * 0.5)
    top = max((v for _, v in rows), default=0) or 1

    for i, (yr, v) in enumerate(rows):
        cx = x0 + slot * i + slot / 2
        bh = (v / top) * 70
        s += (f'<rect x="{cx - bar_w / 2:.1f}" y="{base - bh:.1f}" '
              f'width="{bar_w:.1f}" height="{bh:.1f}" rx="4" fill="url(#g)"/>')
        s += t(cx, base - bh - 7, fmt(v), 10, cls="d", anchor="middle")
        s += t(cx, base + 18, str(yr), 10, cls="d", anchor="middle")
    s += t(20, h - 12, "calendar years since account creation", 10, cls="d")
    s += "</svg>"
    return s


def repos_card(repos) -> str:
    """Five most recently pushed public, non-fork repositories."""
    w, h = 520, 220
    s = svg_open(w, h, "Recently pushed repositories",
                 ("basic-regular", "basic-bold"))
    s += t(20, 30, "recently pushed", 13, weight=700)

    y = 60
    for r in repos[:5]:
        name = r["name"]
        if len(name) > 26:
            name = name[:25] + "\u2026"
        s += f'<circle cx="26" cy="{y - 4}" r="3.2" fill="{DIM}"/>'
        s += t(38, y, name, 12)
        s += t(w - 150, y, f'{r["stars"]} stars', 10, cls="d", anchor="end")
        s += t(w - 20, y, f'pushed {r["days_ago"]}d ago', 10, cls="d",
               anchor="end")
        y += 30
    s += "</svg>"
    return s


# ---------------------------------------------------------------- fetch


CONTRIB_Q = """
query($login:String!,$from:DateTime!,$to:DateTime!){
  user(login:$login){
    contributionsCollection(from:$from,to:$to){
      contributionCalendar{
        totalContributions
        weeks{ firstDay contributionDays{ date contributionCount } }
      }
    }
  }
}
"""

YEAR_Q = """
query($login:String!,$from:DateTime!,$to:DateTime!){
  user(login:$login){
    contributionsCollection(from:$from,to:$to){
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      totalPullRequestReviewContributions
      restrictedContributionsCount
      contributionCalendar{ totalContributions }
    }
  }
}
"""

META_Q = """
query($login:String!){
  user(login:$login){
    createdAt
    followers{ totalCount }
    following{ totalCount }
    repositories(first:1,privacy:PUBLIC,isFork:false,ownerAffiliations:OWNER){
      totalCount
    }
  }
}
"""

MERGED_Q = """
query($q:String!){ search(query:$q,type:ISSUE){ issueCount } }
"""

USER_Q = """
query($login:String!){
  user(login:$login){
    repositories(first:100,isFork:false,privacy:PUBLIC,ownerAffiliations:OWNER,
                 orderBy:{field:PUSHED_AT,direction:DESC}){
      nodes{
        name
        url
        description
        pushedAt
        stargazerCount
        forkCount
        isFork
        isArchived
        primaryLanguage{ name }
        languages(first:10,orderBy:{field:SIZE,direction:DESC}){
          edges{ size node{ name } }
        }
      }
    }
  }
}
"""


def flatten(weeks) -> list:
    days = []
    for w in weeks:
        for d in w["contributionDays"]:
            days.append({"date": d["date"], "count": d["contributionCount"]})
    return days


def weekly(days) -> list:
    weeks = []
    for i in range(0, len(days), 7):
        chunk = days[i:i + 7]
        weeks.append(sum(d["count"] for d in chunk))
    return weeks


def compute_streaks(days) -> dict:
    best = cur = 0
    cur_from = longest_from = longest_to = None
    best_from = None
    run_start = None
    for d in days:
        if d["count"] > 0:
            if run_start is None:
                run_start = d["date"]
            cur += 1
            if cur > best:
                best, best_from = cur, run_start
        else:
            run_start = None
            cur = 0
    if best_from:
        longest_from, longest_to = best_from, days[-1]["date"]
    # current streak = trailing run of non-zero days
    cur = 0
    run_start = None
    for d in reversed(days):
        if d["count"] > 0:
            cur += 1
            run_start = d["date"]
        else:
            break
    return {
        "current": cur,
        "current_from": run_start,
        "longest": best,
        "longest_from": longest_from,
        "longest_to": longest_to,
    }


def year_windows(created_year: int):
    """Half-year windows, each under the API's one-year span limit.

    A leap calendar year is 366 days, which contributionsCollection rejects, so
    every year is queried in two halves and summed. Halves keep the whole-year
    total exact without ever exceeding the limit.
    """
    now = dt.datetime.now(dt.timezone.utc)
    top = now.replace(hour=23, minute=59, second=59, microsecond=0)
    out = []
    for y in range(created_year, now.year + 1):
        halves = [
            (dt.datetime(y, 1, 1, tzinfo=dt.timezone.utc),
             dt.datetime(y, 6, 30, 23, 59, 59, tzinfo=dt.timezone.utc)),
            (dt.datetime(y, 7, 1, tzinfo=dt.timezone.utc),
             dt.datetime(y, 12, 31, 23, 59, 59, tzinfo=dt.timezone.utc)),
        ]
        for frm, end in halves:
            if frm > top:
                continue
            out.append((y, frm, min(end, top)))
    return out


def lifetime(who: str, created_year: int):
    """Sum per-year contribution counts and keep each year's total."""
    sums = {"commits": 0, "prs": 0, "issues": 0, "reviews": 0, "private": 0}
    by_year: dict[int, int] = {}
    for y, frm, to in year_windows(created_year):
        d = gql(YEAR_Q, {"login": who, "from": frm.isoformat(),
                         "to": to.isoformat()})
        c = d["user"]["contributionsCollection"]
        sums["commits"] += c["totalCommitContributions"]
        sums["prs"] += c["totalPullRequestContributions"]
        sums["issues"] += c["totalIssueContributions"]
        sums["reviews"] += c["totalPullRequestReviewContributions"]
        sums["private"] += c["restrictedContributionsCount"]
        by_year[y] = by_year.get(y, 0) + c["contributionCalendar"]["totalContributions"]
    return sums, sorted(by_year.items())


def merged_prs(who: str) -> int:
    q = f"author:{who} type:pr is:merged"
    d = gql(MERGED_Q, {"q": q})
    return int(d["search"]["issueCount"])


def commit_if_changed(files) -> None:
    if not files:
        return
    q = subprocess.run(["git", "status", "--porcelain", "--"] + files,
                       capture_output=True, text=True)
    if not q.stdout.strip():
        print("no change - skipping commit")
        return
    subprocess.run(["git", "config", "user.name", "github-actions[bot]"], check=True)
    subprocess.run(
        ["git", "config", "user.email",
         "41898282+github-actions[bot]@users.noreply.github.com"], check=True)
    subprocess.run(["git", "add", "--"] + files, check=True)
    subprocess.run(["git", "commit", "-m", "stats: refresh"], check=True)
    subprocess.run(["git", "push"], check=True)
    print("committed")


FILES = ["stats.svg", "streak.svg", "langs.svg", "year.svg",
         "profile.svg", "yearly.svg", "repos.svg"]


def card(name: str, build) -> None:
    """A failure in one card must leave its previous SVG in place."""
    try:
        write(name, build())
    except Exception as e:  # noqa: BLE001 - one bad card must not sink the job
        print(f"warning: {name} not updated: {e}")


def main() -> None:
    who = login()
    frm, to = utc_window()
    print(f"window {frm:%Y-%m-%d} .. {to:%Y-%m-%d} (UTC, pinned)")

    days, cal = [], None
    try:
        c = gql(CONTRIB_Q, {"login": who, "from": frm.isoformat(),
                            "to": to.isoformat()})
        cal = c["user"]["contributionsCollection"]["contributionCalendar"]
        days = flatten(cal["weeks"])
    except Exception as e:  # noqa: BLE001
        print(f"warning: contributions fetch failed: {e}")

    user = None
    try:
        user = gql(USER_Q, {"login": who})["user"]
    except Exception as e:  # noqa: BLE001
        print(f"warning: repository fetch failed: {e}")

    meta = None
    try:
        meta = gql(META_Q, {"login": who})["user"]
    except Exception as e:  # noqa: BLE001
        print(f"warning: account fetch failed: {e}")

    global streak_stats
    if days:
        streak_stats = compute_streaks(days)
        totals = {
            "total": cal["totalContributions"],
            "active_days": sum(1 for d in days if d["count"] > 0),
            "weeks": weekly(days),
        }
        card("stats.svg", lambda: hero(days, totals))
        card("streak.svg", lambda: streak(days))
        card("year.svg", lambda: year_svg(days))

    if user:
        card("langs.svg", lambda: langs(user))
        repos = []
        for r in user["repositories"]["nodes"][:5]:
            pushed = dt.datetime.fromisoformat(r["pushedAt"].replace("Z", "+00:00"))
            days_ago = (dt.datetime.now(dt.timezone.utc) - pushed).days
            repos.append({"name": r["name"], "stars": r["stargazerCount"],
                          "days_ago": max(0, days_ago)})
        card("repos.svg", lambda: repos_card(repos))

    per_year, sums = [], None
    if meta:
        try:
            created_year = dt.date.fromisoformat(meta["createdAt"][:10]).year
            sums, per_year = lifetime(who, created_year)
        except Exception as e:  # noqa: BLE001
            print(f"warning: lifetime fetch failed: {e}")

    if meta and sums and user:
        try:
            sums["merged"] = merged_prs(who)
        except Exception as e:  # noqa: BLE001
            print(f"warning: merged PR count failed: {e}")
            sums["merged"] = 0

        nodes = user["repositories"]["nodes"] if user else []
        stars = sum(r["stargazerCount"] for r in nodes
                    if not r["isFork"] and not r["isArchived"])
        years = max(1, dt.date.today().year - created_year + 1)
        data = {
            "commits": sums["commits"],
            "prs": sums["prs"],
            "issues": sums["issues"],
            "reviews": sums["reviews"],
            "stars": stars,
            "public_repos": meta["repositories"]["totalCount"],
            "followers": meta["followers"]["totalCount"],
            "private": sums["private"],
            "years": years,
        }
        print(f"lifetime: {data} merged PRs={sums['merged']}")
        card("profile.svg", lambda: profile_card(data))

    if per_year:
        card("yearly.svg", lambda: yearly_card(per_year))

    commit_if_changed(FILES)


if __name__ == "__main__":
    main()
