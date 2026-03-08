# SchemaWiki - Add to Your Project

## Required Files (2 files)

### File 1: `.github/workflows/schemawiki.yml`

```yaml
name: SchemaWiki

on: [push]

jobs:
  schemawiki:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run SchemaWiki
        run: |
          wget -q https://raw.githubusercontent.com/vkolyvas/SchemaWiki/master/schema_analyzer.py
          chmod +x schema_analyzer.py
          python3 schema_analyzer.py --update
          mkdir -p docs
          cp -r .schemaWiki/* docs/
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          git add .schemaWiki/ docs/ 2>/dev/null || true
          git commit -m "docs: Update SchemaWiki" || exit 0

      - name: Push Changes
        run: |
          git push https://x-access-token:${{ secrets.GITHUB_TOKEN }}@github.com/${{ github.repository }} HEAD:main --force || true
```

### File 2: `docs/index.html`

```html
<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="refresh" content="0; URL=README.html">
    <title>Wiki</title>
</head>
<body>
    <p>Redirecting to <a href="README.html">Wiki</a>...</p>
</body>
</html>
```

## Setup

1. Add both files above to your project
2. Push to GitHub
3. Enable GitHub Pages: **Settings → Pages → Deploy from branch → main → /docs**
