# Reusable GitHub Action to add to ANY project
# Add this to your project's .github/workflows/schemawiki.yml

name: SchemaWiki

on:
  push:
    branches: [main, master]

jobs:
  schemawiki:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run SchemaWiki
        uses: vkolyvas/SchemaWiki/analyze-project.yml@main
        with:
          base_branch: origin/main
          update_wiki: true
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
