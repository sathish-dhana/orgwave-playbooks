---
name: orgwave-confluence-service-doc
description: User provides a service name; create a minimal Confluence page with Java and Spring Boot versions only (Confluence MCP).
---

# Confluence service stub (Java / Spring Boot)

## New here? Confluence MCP in this repo

1. **Pinned server:** **`mcp-servers/servers/confluence.json`** is merged into **`.cursor/mcp.json`** with the rest of the servers. One-time install: **`cd orgwave/mcp-confluence-runtime && npm ci`** (see [mcp-servers/README.md](../../mcp-servers/README.md) → *Confluence*).
2. Set **`CONFLUENCE_BASE_URL`**, **`CONFLUENCE_USER_EMAIL`**, **`CONFLUENCE_API_TOKEN`** in repo-root **`.env`** ([`.env.example`](../../.env.example)).
3. Reload Cursor, enable **`confluence`** under **Tools & MCP**. If tools or auth fail, **[orgwave/required-mcp.md](../../orgwave/required-mcp.md)**.

---

## Prerequisites

- **MCP servers required:** **`confluence`** only. All Confluence steps use **only** Confluence MCP tools (no shell or ad-hoc Confluence REST).
- **Hard stop — missing from `.cursor/mcp.json`:** If **`mcpServers.confluence`** is absent, **stop**. Tell the user to restore **`mcp-servers/servers/confluence.json`**, run **`python3 orgwave/scripts/build-mcp-json.py`**, **`cd orgwave/mcp-confluence-runtime && npm ci`**, reload, enable the server, then continue in a new message.
- **Hard stop — disabled or tools missing:** **Stop** with **[orgwave/required-mcp.md](../../orgwave/required-mcp.md)**. **Do not** substitute REST.
- **Hard stop — auth:** After **one** retry, **401** / **403** → **stop** with token guidance (**[mcp-servers/README.md](../../mcp-servers/README.md)**).

When every prerequisite passes, **continue**.

## 1. Intent

- **Input:** The user provides a **service name** (string). Optionally they also give **Java version** and **Spring Boot version**; if either is missing, **ask once** for the two versions (plain text, e.g. `17`, `3.2.5`).
- **Change:** **Create a new** Confluence page (child of the parent the user specifies) documenting **only**:
  - Service name  
  - Java version  
  - Spring Boot version  
  Nothing else (no architecture, no links, unless the user explicitly asks in the same run).
- **Done when:** Confluence MCP reports success and returns or implies a page URL. **Do not** delete spaces or bulk-edit unrelated pages.

## 2. Inputs (ask if missing)

- **Service name** (required) — from the user message if present.
- **Java version** and **Spring Boot version** — from the user message if present; otherwise ask in one short prompt.
- **Confluence parent** — space key (and parent page id or title) where the new page should be created.

## 3. Page shape

Use whatever body format the Confluence MCP expects (markdown or wiki/storage as supported). Content must be minimal, for example:

```text
Service: <service_name>

Java version: <value>
Spring Boot version: <value>
```

**Title:** `<service_name>` or `Service: <service_name>` — prefer the shorter title unless the user asked otherwise.

## 4. Execution

1. Confirm **service name** and both versions (ask if needed).
2. Confirm **parent** location (space / parent page).
3. Call Confluence MCP **create page** (or equivalent) once per run.
4. Retry the **same** tool **once** on transient failure; if it still fails, **stop** with gate / auth guidance.

## 5. Checklist

- [ ] **`confluence`** prerequisite satisfied or run **stopped** with gate message
- [ ] New page created via **Confluence MCP** only
- [ ] Body contains only service name + Java version + Spring Boot version (plus optional user-requested extras in that same message only)
- [ ] No secrets in the page

## Automation notes

- **Catalog:** [orgwave/catalog.yaml](../../orgwave/catalog.yaml) — `python3 orgwave/scripts/generate-orgwave-deeplink.py --write-docs`
- **MCP:** [mcp-servers/README.md](../../mcp-servers/README.md), [orgwave/required-mcp.md](../../orgwave/required-mcp.md)
