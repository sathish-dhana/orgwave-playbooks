#!/usr/bin/env python3
"""Merge orgwave/mcp/servers/*.json into .cursor/mcp.json (Cursor project MCP config)."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_ORGWAVE_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = _ORGWAVE_DIR.parent
SERVERS_DIR = _ORGWAVE_DIR / "mcp" / "servers"
OUTPUT = REPO_ROOT / ".cursor" / "mcp.json"

_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def load_servers(servers_dir: Path) -> dict[str, dict]:
    if not servers_dir.is_dir():
        raise FileNotFoundError(f"Missing servers directory: {servers_dir}")

    merged: dict[str, dict] = {}
    for path in sorted(servers_dir.glob("*.json")):
        stem = path.stem
        if stem.startswith("_"):
            continue
        if not _ID_RE.match(stem):
            raise ValueError(
                f"Invalid server id from filename {path.name!r}: "
                "use [a-z0-9-]+ starting with a letter or digit (e.g. github.json)."
            )
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError(f"{path}: root must be a JSON object")
        body = {k: v for k, v in raw.items() if k != "_orgwave"}
        if not body:
            raise ValueError(f"{path}: no Cursor config keys (only _orgwave?)")
        if stem in merged:
            raise ValueError(f"Duplicate server id {stem!r}")
        merged[stem] = body
    return merged


def main() -> None:
    p = argparse.ArgumentParser(description="Build .cursor/mcp.json from orgwave/mcp/servers/*.json")
    p.add_argument(
        "--check",
        action="store_true",
        help="Validate server files only; do not write .cursor/mcp.json",
    )
    args = p.parse_args()

    try:
        servers = load_servers(SERVERS_DIR)
    except (OSError, ValueError, json.JSONDecodeError) as e:
        print(f"build-mcp-json: {e}", file=sys.stderr)
        sys.exit(1)

    if not servers:
        print("build-mcp-json: no server JSON files (excluding _*.json)", file=sys.stderr)
        sys.exit(1)

    payload = {"mcpServers": servers}
    text = json.dumps(payload, indent=2) + "\n"

    if args.check:
        print(text, end="")
        return

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(text, encoding="utf-8")
    print(f"Wrote {OUTPUT} ({len(servers)} server(s))")


if __name__ == "__main__":
    main()
