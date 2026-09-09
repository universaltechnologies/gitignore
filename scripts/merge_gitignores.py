#!/usr/bin/env python3
"""Merge official github/gitignore templates and the repo-local user.gitignore
into this repo's own .gitignore.

Usage:
    python scripts/merge_gitignores.py            # fetch upstream templates, regenerate .gitignore
    python scripts/merge_gitignores.py --check    # check only, exit 1 when the file differs
"""

import argparse
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = REPO_ROOT / ".gitignore"

RAW_BASE = "https://raw.githubusercontent.com/github/gitignore/main"

SECTIONS = [
    {
        "title": "Python",
        "source": "https://github.com/github/gitignore/blob/main/Python.gitignore?raw=true",
        "raw_url": f"{RAW_BASE}/Python.gitignore",
        "scope": "Python artifacts (bytecode/virtualenvs/packaging/tool caches/credentials, etc.)",
    },
    {
        "title": "Unity",
        "source": "https://github.com/github/gitignore/blob/main/Unity.gitignore?raw=true",
        "raw_url": f"{RAW_BASE}/Unity.gitignore",
        "scope": "Unity project artifacts (Library/Temp/Obj/Build/Logs/IDE caches, etc.)",
    },
    {
        "title": "User",
        "source": "user.gitignore (repo-local, hand-maintained)",
        "local_path": REPO_ROOT / "user.gitignore",
        "scope": "Personal machine/editor ignores, not fetched from upstream",
    },
]

BANNER_WIDTH = 80
# 5 newlines between blocks = line break + 4 blank lines, keeps sections clearly apart
SECTION_GAP_NEWLINES = 5


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "gitignore-sync-script"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def build_combined() -> str:
    blocks = []
    for idx, sec in enumerate(SECTIONS, start=1):
        banner = "\n".join(
            [
                "#" * BANNER_WIDTH,
                f"# Section {idx}: {sec['title']}",
                f"# Source: {sec['source']}",
                f"# Scope : {sec['scope']}",
                "#" * BANNER_WIDTH,
            ]
        )
        if "local_path" in sec:
            content = sec["local_path"].read_text(encoding="utf-8").rstrip("\n")
        else:
            content = fetch(sec["raw_url"]).rstrip("\n")
        blocks.append(f"{banner}\n\n{content}")
    # single trailing newline at EOF, per POSIX convention
    return ("\n" * SECTION_GAP_NEWLINES).join(blocks) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="check only, do not write the file")
    args = parser.parse_args()

    combined = build_combined()

    existing = OUTPUT_FILE.read_text(encoding="utf-8").replace("\r\n", "\n") if OUTPUT_FILE.exists() else None
    if existing == combined:
        print(".gitignore is already up to date")
        return 0

    if args.check:
        print(".gitignore differs from regenerated content")
        return 1

    OUTPUT_FILE.write_text(combined, encoding="utf-8", newline="\n")
    print(f"Generated {OUTPUT_FILE} ({len(combined.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
