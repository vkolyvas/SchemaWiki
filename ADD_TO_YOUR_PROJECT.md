# SchemaWiki - Add to Your Project

## Required Files (2 files needed)

You need to add these 2 files to your project:

---

### File 1: `.github/workflows/schemawiki.yml`

Create this directory and file in your project:

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

      - name: Copy to docs
        run: |
          mkdir -p docs
          cp -r .schemaWiki/* docs/

      - name: Commit and Push
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          git add .schemaWiki/ docs/ 2>/dev/null || true
          git commit -m "docs: Update SchemaWiki" || exit 0
          git push https://x-access-token:${{ secrets.GITHUB_TOKEN }}@github.com/${{ github.repository }} HEAD:main --force || true
```

---

### File 2: `docs/index.html`

Create a simple redirect page:

```html
<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="refresh" content="0; URL=README.html">
    <title>Wiki Redirect</title>
</head>
<body>
    <p>Redirecting to <a href="README.html">Wiki</a>...</p>
</body>
</html>
```

---

## Setup Steps

### Step 1: Add the 2 files above to your project

### Step 2: Commit and push to GitHub

This will trigger the GitHub Action.

### Step 3: Enable GitHub Pages (REQUIRED)

After the workflow runs:

1. Go to your **Repository Settings**
2. Click **Pages** (in the left sidebar)
3. Under "Build and deployment":
   - **Source**: Select **Deploy from a branch**
   - **Branch**: Select **main** (or master)
   - **Folder**: Select **/docs**
4. Click **Save**

Your wiki will be at:
`https://<your-username>.github.io/<repo-name>/`

---

## Files Summary

| File | Purpose |
|------|---------|
| `.github/workflows/schemawiki.yml` | GitHub Actions workflow |
| `docs/index.html` | Redirect to wiki (you create this) |

The `schema_analyzer.py` is downloaded automatically by the workflow - you don't need to add it manually.

---

## Troubleshooting

**Wiki not showing?**
- Check the Actions tab for errors
- Make sure GitHub Pages is enabled (Step 3 above)
- Verify Source is set to `/docs` folder

**No commits in history?**
- The action needs `fetch-depth: 0` to get full history
- First run analyzes all previous commits

---

## Alternative: Local CLI

If you want to test locally first:

```bash
# Download schema_analyzer.py
wget https://raw.githubusercontent.com/vkolyvas/SchemaWiki/master/schema_analyzer.py
chmod +x schema_analyzer.py

# Run locally
python3 schema_analyzer.py --analyze   # Show what AI did
python3 schema_analyzer.py --update     # Update wiki
```
