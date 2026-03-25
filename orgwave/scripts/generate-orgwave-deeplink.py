#!/usr/bin/env python3
"""Cursor deeplinks for OrgWave — prompts + MCP install (see Cursor docs links in module)."""
from __future__ import annotations

import argparse
import base64
import json
import re
import urllib.parse
from pathlib import Path

MAX_LEN = 8000
# MCP install links embed base64(config); stay below typical URL limits.
MCP_INSTALL_MAX_LEN = 48_000
_ORGWAVE_DIR = Path(__file__).resolve().parent.parent  # orgwave/
REPO_ROOT = _ORGWAVE_DIR.parent
CATALOG = _ORGWAVE_DIR / "catalog.yaml"
RUN_MD = _ORGWAVE_DIR / "docs" / "run-in-cursor.md"
PLAYBOOKS_DIR = REPO_ROOT / "playbooks"
MCP_SERVERS_DIR = REPO_ROOT / "mcp-servers" / "servers"
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

# Blue shields badge for “Add to Cursor” (cursor://…/mcp/install — Cursor opens Install MCP Server dialog).
_MCP_ADD_BADGE_COLOR = "2563eb"


def load_mcp_server_install_body(server_id: str) -> dict:
    """Cursor MCP install `config` is the same JSON object as under mcpServers.<id> (no _orgwave)."""
    path = MCP_SERVERS_DIR / f"{server_id}.json"
    if not path.is_file():
        raise FileNotFoundError(
            f"Missing mcp-servers/servers/{server_id}.json — add it or fix catalog mcp_install."
        )
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: root must be a JSON object")
    return {k: v for k, v in raw.items() if k != "_orgwave"}


def mcp_server_display_title(server_id: str) -> str:
    path = MCP_SERVERS_DIR / f"{server_id}.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    ow = raw.get("_orgwave")
    if isinstance(ow, dict) and isinstance(ow.get("title"), str) and ow["title"].strip():
        return ow["title"].strip()
    return server_id


def mcp_install_config_b64(server_id: str) -> str:
    body = load_mcp_server_install_body(server_id)
    if not body:
        raise ValueError(f"MCP server {server_id!r} has no Cursor fields (only _orgwave?)")
    payload = json.dumps(body, separators=(",", ":"), ensure_ascii=False)
    return base64.standard_b64encode(payload.encode("utf-8")).decode("ascii")


def mcp_install_cursor_url(server_id: str) -> str:
    """cursor://…/mcp/install — https://cursor.com/docs/context/mcp/install-links"""
    config_b64 = mcp_install_config_b64(server_id)
    q = urllib.parse.urlencode({"name": server_id, "config": config_b64})
    url = f"cursor://anysphere.cursor-deeplink/mcp/install?{q}"
    if len(url) > MCP_INSTALL_MAX_LEN:
        raise ValueError(
            f"MCP install URL length {len(url)} exceeds {MCP_INSTALL_MAX_LEN} for server {server_id!r}"
        )
    return url


def mcp_install_https_bridge_href(server_id: str, bridge_base: str) -> str:
    """HTTPS page (e.g. GitHub Pages /docs/mcp-install.html) that links to cursor:// — works from github.com README."""
    config_b64 = mcp_install_config_b64(server_id)
    base = bridge_base.rstrip("/")
    q = urllib.parse.urlencode({"name": server_id, "config": config_b64})
    url = f"{base}/mcp-install.html?{q}"
    if len(url) > MCP_INSTALL_MAX_LEN:
        raise ValueError(
            f"MCP bridge URL length {len(url)} exceeds {MCP_INSTALL_MAX_LEN} for server {server_id!r}"
        )
    return url


def mcp_add_to_cursor_href(server_id: str, mcp_bridge: str | None) -> str:
    if mcp_bridge:
        return mcp_install_https_bridge_href(server_id, mcp_bridge)
    return mcp_install_cursor_url(server_id)


def mcp_add_to_cursor_badge_markdown(
    server_id: str, *, disambiguate: bool, mcp_bridge: str | None
) -> str:
    """Badge href: HTTPS bridge when mcp_bridge is set (GitHub README); else cursor:// (Cursor preview)."""
    title = mcp_server_display_title(server_id)
    if disambiguate:
        label = f"Add_to_Cursor_-_{title.replace(' ', '_')}"
        alt = f"Add to Cursor — {title} MCP"
    else:
        label = "Add_to_Cursor"
        alt = "Add to Cursor"
    img = f"https://img.shields.io/badge/-{label}-{_MCP_ADD_BADGE_COLOR}?style=for-the-badge"
    href = mcp_add_to_cursor_href(server_id, mcp_bridge)
    return f"[![{alt}]({img})]({href})"


def mcp_install_badges_row(server_ids: list[str], mcp_bridge: str | None) -> str:
    if not server_ids:
        return ""
    multi = len(server_ids) > 1
    return " ".join(
        mcp_add_to_cursor_badge_markdown(sid, disambiguate=multi, mcp_bridge=mcp_bridge)
        for sid in server_ids
    )


def validate_mcp_install_ids(all_ids: list[str]) -> None:
    seen = set()
    for sid in all_ids:
        if sid in seen:
            continue
        seen.add(sid)
        load_mcp_server_install_body(sid)

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


def parse_catalog(path: Path) -> tuple[str | None, list[tuple[str, str | None, list[str]]]]:
    """Return (mcp_install_bridge, [(id, name, mcp_install_ids), ...]) from catalog.yaml (no PyYAML)."""
    text = path.read_text(encoding="utf-8")
    bridge: str | None = None
    bm = re.search(r"(?m)^mcp_install_bridge:\s*(.+)$", text)
    if bm:
        raw_b = bm.group(1).strip()
        raw_b = raw_b.split("#")[0].strip().strip("\"'")
        if raw_b and raw_b.lower() not in ("null", "none", "~", "false"):
            bridge = raw_b
    chunks = re.split(r"(?m)^\s*-\s+id:\s*", text)
    out: list[tuple[str, str | None, list[str]]] = []
    for chunk in chunks[1:]:
        first, _, rest = chunk.partition("\n")
        pid = first.strip().strip("\"'")
        if not pid or pid.startswith("#"):
            continue
        nm = re.search(r"(?m)^\s+name:\s*(.+)$", chunk)
        name = nm.group(1).strip().strip("\"'") if nm else None
        mcp_ids: list[str] = []
        mm = re.search(r"(?m)^\s*mcp_install:\s*(.+)$", chunk)
        if mm:
            raw_m = mm.group(1).strip()
            raw_m = raw_m.split("#")[0].strip()
            for part in raw_m.split(","):
                sid = part.strip().strip("\"'")
                if sid:
                    mcp_ids.append(sid)
        out.append((pid, name, mcp_ids))
    return bridge, out


def markdown_buttons(
    entries: list[tuple[str, str | None, list[str]]], mcp_bridge: str | None
) -> str:
    bridge_note = ""
    if mcp_bridge:
        bridge_note = (
            "Blue **Add to Cursor** uses an **HTTPS** helper (GitHub Pages `docs/mcp-install.html`) so the link works from **github.com**. On that page, click **Add to Cursor** to open the install dialog ([MCP install links](https://cursor.com/docs/context/mcp/install-links))."
        )
    else:
        bridge_note = (
            "**Add to Cursor** targets `cursor://` — that works in the **Cursor** app’s Markdown preview. **On github.com**, image badges are often opened via **Camo** and `cursor://` may not run; set **`mcp_install_bridge`** in **`orgwave/catalog.yaml`** to your **GitHub Pages** origin and regenerate (see **`docs/README.md`**), or use your org’s HTTPS install page the same way."
        )
    lines = [
        "# Run in Cursor",
        "",
        "One click opens Cursor with a **prefilled prompt** for that playbook (you still confirm before it runs).",
        bridge_note,
        "**Open the `orgwave-playbooks` folder** in Cursor first so `${workspaceFolder}` in `command` / `args` resolves.",
        "",
        "| Playbook | Add to Cursor (MCP) | Run |",
        "|----------|---------------------|-----|",
    ]
    for pid, name, mcp_ids in entries:
        label = name or pid
        install_cell = (
            mcp_install_badges_row(mcp_ids, mcp_bridge) if mcp_ids else "—"
        )
        lines.append(
            f"| **{label}** (`{pid}`) | {install_cell} | {run_in_cursor_badge(web_url(pid))} |"
        )
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
    """Extra markdown appended to generated README — terminal snippets (zshrc / .env)."""
    if playbook_id == "confluence-service-doc":
        return "\n".join(
            [
                "## Terminal: Confluence email and token (`~/.zshrc`)",
                "",
                "**`CONFLUENCE_BASE_URL`** is pinned in **`mcp-servers/servers/confluence.json`** (`https://confluence.myntracorp.com/`). **`confluence-mcp-launch.mjs`** sources **`~/.zshrc`** when repo **`.env`** does not set these vars (good for Dock / deep links). Append **email** and **token** once (replace placeholders). Same rule as GitHub MCP: keep **`~/.zshrc`** from printing to stdout on non-interactive load (stray **`echo`** can break the launcher’s probe):",
                "",
                "```bash",
                "umask 077",
                "cat >> ~/.zshrc <<'EOF'",
                "",
                "# OrgWave Confluence MCP — do not commit this file",
                'export CONFLUENCE_USER_EMAIL="you@myntracorp.com"',
                'export CONFLUENCE_API_TOKEN="your_confluence_personal_access_token"',
                "EOF",
                "```",
                "",
                "Then **`source ~/.zshrc`** (optional), **Developer: Reload Window**, and enable **`confluence`** under Tools & MCP. Run **`python3 orgwave/scripts/build-mcp-json.py`** only if you changed **`mcp-servers/servers/*.json`**.",
                "",
                "**Optional — repo `.env` instead:** same variable names in **`.env`** at the repo root (see **[`.env.example`](../../.env.example)**). **Alternatively:** **`~/.cursor/confluence-mcp.env`** — see **[mcp-servers/README.md](../../mcp-servers/README.md)**.",
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


def playbook_readme_body(
    playbook_id: str,
    title: str,
    mcp_install_ids: list[str],
    mcp_bridge: str | None,
) -> str:
    badge = run_in_cursor_badge(web_url(playbook_id))
    paste_fallback = build_prompt(playbook_id)
    extra = playbook_readme_env_section(playbook_id)
    install_block: list[str] = []
    if mcp_install_ids:
        install_block = [
            mcp_install_badges_row(mcp_install_ids, mcp_bridge),
            "",
        ]
        if not mcp_bridge:
            install_block.extend(
                [
                    "> **On github.com:** the badge may open a **Camo** image URL instead of Cursor — GitHub often does not apply `cursor://` links on image badges. Set **`mcp_install_bridge`** in **`orgwave/catalog.yaml`** (see **`docs/README.md`**) and regenerate, or open this README in **Cursor**.",
                    "",
                ]
            )
        bridge_hint = (
            "Opens the **[MCP install](https://cursor.com/docs/context/mcp/install-links)** flow (prefilled name, command, env)."
            if not mcp_bridge
            else "Opens an **HTTPS** helper page; click **Add to Cursor** there to launch the install dialog (same as a standalone setup page)."
        )
        install_block.append(
            f"**Add to Cursor:** {bridge_hint} Open **`orgwave-playbooks`** as the workspace folder first so paths like `${{workspaceFolder}}/orgwave/scripts/...` work. Fill secrets in the dialog or use **`.env`** / **`~/.cursor/*-mcp.env`** / **`~/.zshrc`** as in **[mcp-servers/README.md](../../mcp-servers/README.md)**."
        )
        install_block.append("")
    return "\n".join(
        [
            README_MARKER,
            f"# {title}",
            "",
            f"Playbook id: `{playbook_id}`",
            "",
            *install_block,
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


def write_playbook_readmes(
    entries: list[tuple[str, str | None, list[str]]], mcp_bridge: str | None
) -> list[Path]:
    """Write playbooks/<id>/README.md for each catalog entry when that folder exists."""
    catalog_ids = {pid for pid, _, _ in entries}
    written: list[Path] = []

    for pid, name, mcp_ids in entries:
        folder = PLAYBOOKS_DIR / pid
        if not folder.is_dir():
            continue
        readme = folder / "README.md"
        readme.write_text(
            playbook_readme_body(pid, name or pid, mcp_ids, mcp_bridge), encoding="utf-8"
        )
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
        "--mcp-install",
        metavar="SERVER_ID",
        help="Print cursor:// MCP install URL for mcp-servers/servers/<id>.json (see Cursor MCP install links)",
    )
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
    p.add_argument(
        "--mcp-bridge",
        metavar="HTTPS_ORIGIN",
        help="Override catalog mcp_install_bridge for this run (e.g. https://org.github.io/repo — no trailing slash)",
    )
    args = p.parse_args()

    if args.mcp_install:
        print(mcp_install_cursor_url(args.mcp_install))
        return

    if args.write_docs or args.print_all:
        catalog_bridge, entries = parse_catalog(CATALOG)
        mcp_bridge = (args.mcp_bridge or catalog_bridge or "").strip().rstrip("/") or None
        flat_mcp: list[str] = []
        for _pid, _n, ids in entries:
            flat_mcp.extend(ids)
        validate_mcp_install_ids(flat_mcp)
        body = markdown_buttons(entries, mcp_bridge)
        if args.print_all:
            print(body, end="")
        else:
            RUN_MD.parent.mkdir(parents=True, exist_ok=True)
            RUN_MD.write_text(body, encoding="utf-8")
            print(f"Wrote {RUN_MD}")
            readmes = write_playbook_readmes(entries, mcp_bridge)
            for r in readmes:
                print(f"Wrote {r}")
        return

    if not args.playbook_id:
        p.error("pass playbook_id, or use --write-docs / --print-all / --mcp-install")
    if args.desktop:
        print(desktop_url(args.playbook_id))
    else:
        print(web_url(args.playbook_id))


if __name__ == "__main__":
    main()
