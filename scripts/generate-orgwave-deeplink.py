#!/usr/bin/env python3
"""Print a https://cursor.com/link/prompt URL to open Cursor with an OrgWave prompt prefilled.

Usage:
  python3 scripts/generate-orgwave-deeplink.py example-migration
  python3 scripts/generate-orgwave-deeplink.py my-playbook --web   # default is web (GitHub-friendly)

Cursor docs: https://cursor.com/docs/reference/deeplinks
Deeplinks do not auto-run; the user reviews and confirms in Cursor.
"""
from __future__ import annotations

import argparse
import urllib.parse

MAX_LEN = 8000


def build_prompt(playbook_id: str) -> str:
    return f"""You are running OrgWave. Open this orgwave-playbooks repository as the Cursor workspace (clone it first if needed).

1. Follow .cursor/rules/orgwave-orchestrator.mdc and load playbook id `{playbook_id}` from catalog.yaml and playbooks/{playbook_id}/SKILL.md.
2. Ask me for the GitHub org if unknown. Use global GitHub MCP to list/filter repos per the playbook (or use a discovery JSON file from the latest Actions run if I attach it).
3. Show a numbered table of candidate services and STOP until I select which repos to run.
4. For each selected service: apply the playbook, run tests if applicable, push branches, open one PR per service. Do not merge."""


def main() -> None:
    p = argparse.ArgumentParser(description="Generate Cursor prompt deeplink for OrgWave")
    p.add_argument("playbook_id", help="Playbook folder name under playbooks/")
    p.add_argument(
        "--desktop",
        action="store_true",
        help="Use cursor:// URL instead of https://cursor.com/link/ (for local use)",
    )
    args = p.parse_args()

    text = build_prompt(args.playbook_id)
    q = urllib.parse.urlencode({"text": text})
    if args.desktop:
        url = f"cursor://anysphere.cursor-deeplink/prompt?{q}"
    else:
        url = f"https://cursor.com/link/prompt?{q}"

    if len(url) > MAX_LEN:
        raise SystemExit(f"URL length {len(url)} exceeds Cursor limit {MAX_LEN}; shorten the prompt template.")
    print(url)


if __name__ == "__main__":
    main()
