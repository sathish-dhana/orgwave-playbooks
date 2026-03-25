# GitHub Pages (`docs/`)

This folder can be published so playbook README **Add to Cursor** buttons work from **github.com** (HTTPS → your click opens a real page with a **`cursor://`** link). GitHub’s README renderer often **does not apply `cursor://`** to image links; clicks then open the badge image via **Camo** instead of Cursor.

## Enable Pages (org/repo)

1. Repo **Settings → Pages → Build and deployment**
2. Source: deploy from branch **main** (or default), folder **`/docs`**
3. Note the site URL, e.g. `https://YOUR_ORG.github.io/YOUR_REPO/`

## Wire OrgWave

Set **`mcp_install_bridge:`** in **`orgwave/catalog.yaml`** to that origin **without a trailing slash**, then:

```bash
python3 orgwave/scripts/generate-orgwave-deeplink.py --write-docs
```

Commit the updated `playbooks/**/README.md` and **`orgwave/docs/run-in-cursor.md`**.

## What gets served

- **`mcp-install.html`** — query params **`name`** (MCP server id) and **`config`** (base64 JSON, same as [Cursor MCP install links](https://cursor.com/docs/context/mcp/install-links)). The page shows an **Add to Cursor** button that points at `cursor://anysphere.cursor-deeplink/mcp/install?…`.
