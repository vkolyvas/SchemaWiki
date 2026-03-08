# SchemaWiki - Add to Your Project

## Quick Start (Only 2 Files Needed)

### Option 1: GitHub Action

Create `.github/workflows/schemawiki.yml`:

```yaml
name: SchemaWiki

on: [push]

jobs:
  schemawiki:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run SchemaWiki
        run: |
          wget -q https://raw.githubusercontent.com/vkolyvas/SchemaWiki/master/schema_analyzer.py
          chmod +x schema_analyzer.py
          python3 schema_analyzer.py --update

      - name: Commit Wiki
        if: success()
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          git add .schemaWiki/ 2>/dev/null || true
          git commit -m "docs: Update SchemaWiki" || exit 0
          git push https://x-access-token:${{ secrets.GITHUB_TOKEN }}@github.com/${{ github.repository }} HEAD:main || true
```

### Option 2: Local CLI

```bash
# Download schema_analyzer.py
wget https://raw.githubusercontent.com/vkolyvas/SchemaWiki/master/schema_analyzer.py
chmod +x schema_analyzer.py

# Run locally
python3 schema_analyzer.py --analyze   # Show what AI did
python3 schema_analyzer.py --update     # Update wiki
```

---

## What It Does

1. Analyzes git commits and diffs
2. Detects feature/fix type from commit messages
3. Updates `.schemaWiki/README.md` with:
   - What files were added/modified/deleted
   - What feature was worked on
   - Commit details

---

## Result

Each project gets `.schemaWiki/README.md`:

```markdown
# Project Wiki

## Feature: user authentication
**Branch:** feature/auth

### Added Files
- auth.py
- models.py

### Modified Files
- app.py

---

## Feature: API fix
**Branch:** fix/pagination
- Modified: api/routes.py
```

---

## Full SchemaWiki (Optional)

For full wiki features with MCP server, see:
- `wiki_tool.py` - CLI for rich wiki creation
- `mcp_server.py` - MCP server for AI agents
