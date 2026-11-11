#!/usr/bin/env python3
"""Update README.md with the newest public repositories.

Fetches repos via the GitHub API (sorted by created, newest first), excludes
forks, archived repos, and the profile repo itself, takes the newest 6, and
rewrites ONLY the content between <!-- REPOS:START --> and <!-- REPOS:END -->
as a Markdown table (Repository | About | Language).

Uses only the standard library. Reads GITHUB_TOKEN and GH_LOGIN from env.
"""

import json
import os
import pathlib
import re
import sys
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
START = "<!-- REPOS:START -->"
END = "<!-- REPOS:END -->"


def fetch_repos(login: str, token: str | None) -> list[dict]:
    repos: list[dict] = []
    page = 1
    while True:
        params = urllib.parse.urlencode(
            {"type": "owner", "sort": "created", "direction": "desc", "per_page": 100, "page": page}
        )
        url = f"https://api.github.com/users/{login}/repos?{params}"
        req = urllib.request.Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "profile-readme-updater",
                **({"Authorization": f"Bearer {token}"} if token else {}),
            },
        )
        with urllib.request.urlopen(req) as resp:
            batch = json.load(resp)
        if not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return repos


def build_table(repos: list[dict], login: str) -> str:
    profile = login.lower()
    rows = []
    for r in repos:
        if r.get("fork") or r.get("archived"):
            continue
        if r.get("name", "").lower() == profile:
            continue
        name = r.get("name", "")
        url = r.get("html_url", "")
        about = (r.get("description") or "").replace("|", "\\|").replace("\n", " ").strip()
        lang = r.get("language") or ""
        rows.append(f"| [{name}]({url}) | {about} | {lang} |")
        if len(rows) >= 6:
            break
    if not rows:
        return "\n_No repositories found._\n"
    header = "| Repository | About | Language |\n| :-- | :-- | :-- |"
    return "\n" + header + "\n" + "\n".join(rows) + "\n"


def main() -> int:
    login = os.environ.get("GH_LOGIN") or os.environ.get("GITHUB_REPOSITORY_OWNER")
    if not login:
        print("GH_LOGIN is required", file=sys.stderr)
        return 2
    token = os.environ.get("GITHUB_TOKEN")

    repos = fetch_repos(login, token)
    table = build_table(repos, login)

    text = README.read_text(encoding="utf-8")
    pattern = re.compile(rf"{re.escape(START)}.*?{re.escape(END)}", re.S)
    if not pattern.search(text):
        print("REPOS markers not found in README.md", file=sys.stderr)
        return 1
    new = pattern.sub(f"{START}{table}{END}", text)
    if new != text:
        README.write_text(new, encoding="utf-8")
        print("README.md updated")
    else:
        print("README.md unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
