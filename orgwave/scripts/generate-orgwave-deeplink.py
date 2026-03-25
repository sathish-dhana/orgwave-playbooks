#!/usr/bin/env python3
"""Cursor prompt deeplinks for OrgWave — https://cursor.com/docs/reference/deeplinks (confirm to run)."""
from __future__ import annotations

import argparse
import base64
import re
import urllib.parse
from pathlib import Path

MAX_LEN = 8000
_ORGWAVE_DIR = Path(__file__).resolve().parent.parent  # orgwave/
REPO_ROOT = _ORGWAVE_DIR.parent
CATALOG = _ORGWAVE_DIR / "catalog.yaml"
RUN_MD = _ORGWAVE_DIR / "docs" / "run-in-cursor.md"
PLAYBOOKS_DIR = REPO_ROOT / "playbooks"
# First line marker so we only overwrite/delete our own READMEs under playbooks/<id>/
README_MARKER = "<!-- orgwave-generated -->"

# Single place for “Run in Cursor” badge markup (used for every playbook row).
# for-the-badge = larger; green background; white ▶ via embedded SVG (play-button look).
RUN_BUTTON_ALT = "Play — Run in Cursor"


def _shields_run_badge_url() -> str:
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
        '<path fill="#fff" d="M8 5v14l11-7z"/>'
        "</svg>"
    )
    logo = "data:image/svg+xml;base64," + base64.standard_b64encode(svg.encode()).decode()
    q = urllib.parse.urlencode({"style": "for-the-badge", "logo": logo})
    return f"https://img.shields.io/badge/-Run_in_Cursor-22c55e?{q}"


RUN_BUTTON_BADGE_IMAGE = _shields_run_badge_url()

# Short plain-text only. No backticks, semicolons in the body, or markdown — Cursor has known deeplink
# parsing bugs (invalid text for prompt) with some characters and with + vs space encoding; see forum
# e.g. https://forum.cursor.com/t/error-handling-deep-link-invalid-text-for-prompt/149270
DEEPLINK_PROMPT_TEMPLATE = (
    "OrgWave: open orgwave-playbooks as workspace. "
    "Run orchestrator rule and playbook {playbook_id}. "
    "Read orgwave/catalog.yaml playbooks/{playbook_id}/SKILL.md and orgwave/required-mcp.md. "
    "Complete Prerequisites in playbooks/{playbook_id}/SKILL.md first. "
    "For each MCP server id listed under MCP servers required confirm mcpServers that id exists in repo root dot cursor mcp dot json. "
    "If a required id is missing stop tell user add mcp-servers/servers that id dot json per mcp-servers README run python3 orgwave/scripts/build-mcp-json.py reload Cursor enable the server. "
    "If a required server is disabled tools missing in session or PAT auth fails after one retry stop with orgwave/required-mcp.md gate and mcp-servers README then user fixes and Reload Window. "
    "If all prerequisites pass continue using only those MCP servers for steps the playbook assigns to them no gh git or ad hoc GitHub REST. "
    "GitHub token for MCP child github-mcp-launch merges envFile dot env github-mcp dot env and zshrc when keys empty see mcp-servers README. "
    "search_repositories does not include permissions push per row say so in the table. "
    "Resolve default branch from MCP metadata if Not Found on file branch or PR base try master then main. "
    "Discover repos numbered table stop for my selection one PR per repo do not merge."
)


def run_in_cursor_badge(deeplink_url: str) -> str:
    """Common markdown for one Run-in-Cursor control (shields badge → deeplink)."""
    return f"[![{RUN_BUTTON_ALT}]({RUN_BUTTON_BADGE_IMAGE})]({deeplink_url})"


def build_prompt(playbook_id: str) -> str:
    return DEEPLINK_PROMPT_TEMPLATE.format(playbook_id=playbook_id)


def _encode_prompt_query(playbook_id: str) -> str:
    # Use percent-encoding for spaces (%20) not + — some Cursor builds mishandle + in prompt text query values.
    return "text=" + urllib.parse.quote(build_prompt(playbook_id), safe="")


def web_url(playbook_id: str) -> str:
    q = _encode_prompt_query(playbook_id)
    url = f"https://cursor.com/link/prompt?{q}"
    if len(url) > MAX_LEN:
        raise ValueError(f"URL length {len(url)} exceeds {MAX_LEN} for playbook {playbook_id!r}")
    return url


def desktop_url(playbook_id: str) -> str:
    q = _encode_prompt_query(playbook_id)
    url = f"cursor://anysphere.cursor-deeplink/prompt?{q}"
    if len(url) > MAX_LEN:
        raise ValueError(f"Desktop URL length {len(url)} exceeds {MAX_LEN} for playbook {playbook_id!r}")
    return url


def parse_catalog(path: Path) -> list[tuple[str, str | None]]:
    """Return [(id, name), ...] from catalog.yaml (no PyYAML dependency)."""
    text = path.read_text(encoding="utf-8")
    chunks = re.split(r"(?m)^\s*-\s+id:\s*", text)
    out: list[tuple[str, str | None]] = []
    for chunk in chunks[1:]:
        first, _, rest = chunk.partition("\n")
        pid = first.strip().strip("\"'")
        if not pid or pid.startswith("#"):
            continue
        nm = re.search(r"(?m)^\s+name:\s*(.+)$", chunk)
        name = nm.group(1).strip().strip("\"'") if nm else None
        out.append((pid, name))
    return out


def markdown_buttons(entries: list[tuple[str, str | None]]) -> str:
    lines = [
        "# Run in Cursor",
        "",
        "One click opens Cursor with a **prefilled prompt** for that playbook (you still confirm before it runs).",
        "",
        "| Playbook | Run |",
        "|----------|-----|",
    ]
    for pid, name in entries:
        label = name or pid
        lines.append(f"| **{label}** (`{pid}`) | {run_in_cursor_badge(web_url(pid))} |")
    lines.extend(
        [
            "",
            "---",
            "",
            "**Do not edit this file by hand.** It is produced from `orgwave/catalog.yaml` by",
            "`orgwave/scripts/generate-orgwave-deeplink.py`.",
            "",
            "Regenerate after catalog or script changes (repo root):",
            "",
            "```bash",
            "python3 orgwave/scripts/generate-orgwave-deeplink.py --write-docs",
            "```",
            "",
        ]
    )
    return "\n".join(lines) + "\n"


def playbook_readme_env_section(playbook_id: str) -> str:
    """Extra markdown appended to generated README — terminal snippets for `.env` setup."""
    if playbook_id == "confluence-service-doc":
        return "\n".join(
            [
                "## Terminal: Confluence email and token (repo `.env`)",
                "",
                "**`CONFLUENCE_BASE_URL`** is pinned in **`mcp-servers/servers/confluence.json`** (`https://confluence.myntracorp.com/`). From the **repo root**, append **email** and **token** only (replace placeholders):",
                "",
                "```bash",
                "cd /path/to/orgwave-playbooks",
                "umask 077",
                "cat >> .env << 'EOF'",
                "CONFLUENCE_USER_EMAIL=you@myntracorp.com",
                "CONFLUENCE_API_TOKEN=your_confluence_personal_access_token",
                "EOF",
                "```",
                "",
                "Then **`python3 orgwave/scripts/build-mcp-json.py`** if you changed server JSON, **Developer: Reload Window**, and enable **`confluence`** under Tools & MCP. Details: **[mcp-servers/README.md](../../mcp-servers/README.md)**.",
                "",
            ]
        )
    if playbook_id == "readme-cursor-smoke-test":
        return "\n".join(
            [
                "## Terminal: GitHub PAT only (repo `.env`)",
                "",
                "This playbook uses **GitHub MCP** only. From the **repo root**:",
                "",
                "```bash",
                "cd /path/to/orgwave-playbooks",
                "umask 077",
                "cat >> .env << 'EOF'",
                "GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_github_pat",
                "EOF",
                "```",
                "",
                "Alternatives: **`~/.cursor/github-mcp.env`**, **`gh auth login`**, or **`~/.zshrc`** `GITHUB_TOKEN` — see **[mcp-servers/README.md](../../mcp-servers/README.md)**. Reload Cursor after editing.",
                "",
            ]
        )
    return ""


def playbook_readme_body(playbook_id: str, title: str) -> str:
    badge = run_in_cursor_badge(web_url(playbook_id))
    paste_fallback = build_prompt(playbook_id)
    extra = playbook_readme_env_section(playbook_id)
    return "\n".join(
        [
            README_MARKER,
            f"# {title}",
            "",
            f"Playbook id: `{playbook_id}`",
            "",
            badge,
            "",
            "Click the **play** button to open Cursor with this playbook's prompt prefilled - you still confirm before the agent runs.",
            "",
            "If Cursor shows **invalid text for prompt**, paste this into Agent chat instead:",
            "",
            "```text",
            paste_fallback,
            "```",
            "",
            f"- Agent instructions: **[SKILL.md](SKILL.md)**",
            f"- All playbooks: **[orgwave/docs/run-in-cursor.md](../../orgwave/docs/run-in-cursor.md)**",
            "",
            "---",
            "",
            "*Auto-generated from `orgwave/catalog.yaml` — do not edit the block above by hand. Regenerate with* "
            "`python3 orgwave/scripts/generate-orgwave-deeplink.py --write-docs`*.*",
            "",
            extra,
        ]
    )


def write_playbook_readmes(entries: list[tuple[str, str | None]]) -> list[Path]:
    """Write playbooks/<id>/README.md for each catalog entry when that folder exists."""
    catalog_ids = {pid for pid, _ in entries}
    written: list[Path] = []

    for pid, name in entries:
        folder = PLAYBOOKS_DIR / pid
        if not folder.is_dir():
            continue
        readme = folder / "README.md"
        readme.write_text(playbook_readme_body(pid, name or pid), encoding="utf-8")
        written.append(readme)

    # Remove stale generated READMEs (playbook removed from catalog)
    if PLAYBOOKS_DIR.is_dir():
        for readme in PLAYBOOKS_DIR.glob("*/README.md"):
            try:
                first = readme.read_text(encoding="utf-8").splitlines()[:1]
            except OSError:
                continue
            if first != [README_MARKER]:
                continue
            parent_id = readme.parent.name
            if parent_id not in catalog_ids:
                readme.unlink(missing_ok=True)

    return written


def main() -> None:
    p = argparse.ArgumentParser(description="Generate Cursor deeplinks for OrgWave playbooks")
    p.add_argument("playbook_id", nargs="?", help="Single playbook id (folder under playbooks/)")
    p.add_argument("--desktop", action="store_true", help="Emit cursor:// URL for one id")
    p.add_argument(
        "--write-docs",
        action="store_true",
        help="Write orgwave/docs/run-in-cursor.md and playbooks/<id>/README.md (folder landing + Run badge)",
    )
    p.add_argument(
        "--print-all",
        action="store_true",
        help="Print markdown table to stdout (same as --write-docs but no file)",
    )
    args = p.parse_args()

    if args.write_docs or args.print_all:
        entries = parse_catalog(CATALOG)
        body = markdown_buttons(entries)
        if args.print_all:
            print(body, end="")
        else:
            RUN_MD.parent.mkdir(parents=True, exist_ok=True)
            RUN_MD.write_text(body, encoding="utf-8")
            print(f"Wrote {RUN_MD}")
            readmes = write_playbook_readmes(entries)
            for r in readmes:
                print(f"Wrote {r}")
        return

    if not args.playbook_id:
        p.error("pass playbook_id, or use --write-docs / --print-all")
    if args.desktop:
        print(desktop_url(args.playbook_id))
    else:
        print(web_url(args.playbook_id))


if __name__ == "__main__":
    main()
