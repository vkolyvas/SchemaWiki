#!/usr/bin/env python3
"""
SchemaWiki Analyzer - Analyzes AI agent sessions and updates project wikis
Can be used as:
  1. GitHub Action (auto-run on push)
  2. CLI tool in any project
  3. MCP tool in Claude Code
"""

import argparse
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Config
WIKI_DIR = ".schemaWiki"
FEATURES_DIR = ".schemaWiki/features"
DEFAULT_BRANCH = "main"

# Threshold for creating new feature page (LOC = lines of code)
LOC_THRESHOLD = 50  # Changes > 50 LOC create new feature page


def run_cmd(cmd: list) -> tuple:
    """Run shell command and return output."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), 1


def get_current_branch() -> str:
    """Get current git branch."""
    stdout, _, _ = run_cmd(["git", "branch", "--show-current"])
    return stdout.strip() or "main"


def get_last_commit() -> dict:
    """Get last commit info."""
    stdout, _, rc = run_cmd(["git", "log", "-1", "--format=%H|%s|%b|%an|%ae|%ai", "--name-only"])
    if rc or not stdout:
        return {}

    lines = stdout.strip().split("\n")
    parts = lines[0].split("|")

    return {
        "hash": parts[0] if len(parts) > 0 else "",
        "subject": parts[1] if len(parts) > 1 else "",
        "body": parts[2] if len(parts) > 2 else "",
        "author": parts[3] if len(parts) > 3 else "",
        "email": parts[4] if len(parts) > 4 else "",
        "date": parts[5] if len(parts) > 5 else "",
        "files": [
            l
            for l in lines[1:]
            if l.strip()
            and not l.startswith("-")
            and not l.startswith("|")
            and "Co-Authored-By" not in l
        ],
    }


def get_diff_since(base_branch: str = None) -> list:
    """Get files changed since base branch/tag."""
    branch = base_branch or f"origin/{DEFAULT_BRANCH}"

    # Try merge-base to find where we diverged
    stdout, _, rc = run_cmd(["git", "merge-base", "HEAD", branch])
    if rc:
        # Fallback: just get last commit's files
        commit = get_last_commit()
        return [{"file": f, "status": "M"} for f in commit.get("files", [])]

    base = stdout.strip()
    stdout, _, _ = run_cmd(["git", "diff", "--name-status", f"{base}..HEAD"])

    changes = []
    for line in stdout.strip().split("\n"):
        if line:
            parts = line.split("\t")
            if len(parts) >= 2:
                changes.append({"status": parts[0], "file": parts[1]})
    return changes


def calculate_loc_changes(base_branch: str = None) -> dict:
    """Calculate lines of code added/deleted per file."""
    branch = base_branch or "HEAD~1"  # Default to last commit if no base

    # Try merge-base first, fallback to last commit
    stdout, _, rc = run_cmd(["git", "merge-base", "HEAD", branch.replace("origin/", "origin/")])

    if rc or not stdout.strip():
        # Use last commit as base
        stdout, _, _ = run_cmd(["git", "rev-parse", "HEAD~1"])
        if rc or not stdout.strip():
            return {"total_added": 0, "total_deleted": 0, "files": []}

    base = stdout.strip()

    # Use --numstat for accurate numbers (additions, deletions, file)
    stdout, _, rc = run_cmd(["git", "diff", "--numstat", f"{base}..HEAD"])
    if rc:
        return {"total_added": 0, "total_deleted": 0, "files": []}

    total_added = 0
    total_deleted = 0
    file_changes = []

    for line in stdout.strip().split("\n"):
        if line.strip():
            parts = line.split("\t")
            if len(parts) >= 3:
                try:
                    added = int(parts[0]) if parts[0] != "-" else 0
                    deleted = int(parts[1]) if parts[1] != "-" else 0
                    filename = parts[2]

                    total_added += added
                    total_deleted += deleted
                    file_changes.append({"file": filename, "added": added, "deleted": deleted})
                except (ValueError, IndexError):
                    pass

    return {
        "total_added": total_added,
        "total_deleted": total_deleted,
        "total_changes": total_added + total_deleted,
        "files": file_changes,
    }


def is_significant_change(loc_data: dict, feature: dict = None) -> bool:
    """Determine if change is significant enough for new feature page."""
    total = loc_data.get("total_changes", 0)
    files_count = len(loc_data.get("files", []))

    # Big if: > 50 LOC or > 5 files changed
    if total > LOC_THRESHOLD or files_count > 5:
        return True

    # Also big if it's explicitly a feature/feat commit
    if feature and feature.get("type") == "feature":
        return True

    return False


def detect_feature_from_commits() -> Optional[dict]:
    """Detect what feature was worked on from commit messages."""
    stdout, _, rc = run_cmd(["git", "log", "--oneline", "-10"])
    if rc:
        return None

    # Look for patterns like "feat: add user auth", "fix: bug in..."
    patterns = {
        "feature": r"(?:feat|feature|add):?\s+(.+)",
        "fix": r"(?:fix|bug|hotfix):?\s+(.+)",
        "refactor": r"(?:refactor|cleanup):?\s+(.+)",
        "docs": r"(?:docs|doc):?\s+(.+)",
        "test": r"(?:test|spec):?\s+(.+)",
    }

    for line in stdout.strip().split("\n"):
        for ptype, pattern in patterns.items():
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                return {"type": ptype, "title": match.group(1).strip(), "full_message": line}

    return None


def analyze_ai_activity() -> dict:
    """Analyze what the AI agent did."""
    feature = detect_feature_from_commits()
    loc_data = calculate_loc_changes()

    activity = {
        "commit": get_last_commit(),
        "changes": get_diff_since(),
        "feature": feature,
        "branch": get_current_branch(),
        "timestamp": datetime.now().isoformat(),
        "loc": loc_data,
    }

    # Determine if this is a significant change
    activity["is_significant"] = is_significant_change(loc_data, feature)

    # Categorize changes
    categories = {"added": [], "modified": [], "deleted": [], "other": []}
    for change in activity["changes"]:
        status = change.get("status", "M")
        file = change.get("file", "")
        if status == "A":
            categories["added"].append(file)
        elif status == "D":
            categories["deleted"].append(file)
        elif status == "M":
            categories["modified"].append(file)
        else:
            categories["other"].append(file)

    activity["categories"] = categories
    return activity


def read_existing_wiki() -> str:
    """Read existing wiki/docs from project."""
    wiki_path = Path(WIKI_DIR) / "README.md"

    # Also check common locations
    if not wiki_path.exists():
        for alt in ["docs/README.md", "wiki/Home.md", "WIKI.md"]:
            if Path(alt).exists():
                wiki_path = Path(alt)
                break

    if wiki_path.exists():
        return wiki_path.read_text()
    return ""


def generate_wiki_update(activity: dict) -> str:
    """Generate wiki update based on AI activity."""
    commit = activity.get("commit", {})
    feature = activity.get("feature", {})
    categories = activity.get("categories", {})
    branch = activity.get("branch", "unknown")

    updates = []

    # Header
    updates.append(f"\n---\n**Updated:** {activity['timestamp']}\n")

    # Feature/Change detected
    if feature:
        updates.append(f"\n## {feature['type'].title()}: {feature['title']}\n")
        updates.append(f"**Branch:** `{branch}`")
        updates.append(f"**Commit:** `{commit.get('subject', 'N/A')}`")

    # Files changed summary
    if categories.get("added"):
        updates.append("\n### Added Files\n")
        for f in categories["added"]:
            updates.append(f"- `{f}`")

    if categories.get("modified"):
        updates.append("\n### Modified Files\n")
        for f in categories["modified"]:
            updates.append(f"- `{f}`")

    if categories.get("deleted"):
        updates.append("\n### Deleted Files\n")
        for f in categories["deleted"]:
            updates.append(f"- `{f}`")

    # Commit details
    if commit.get("body"):
        updates.append(f"\n### Details\n{commit['body']}\n")

    return "\n".join(updates)


def update_wiki(activity: dict):
    """Update the project wiki with new activity."""
    wiki_path = Path(WIKI_DIR)
    wiki_path.mkdir(exist_ok=True)

    features_path = Path(FEATURES_DIR)
    features_path.mkdir(exist_ok=True)

    readme = wiki_path / "README.md"

    # Get feature info
    feature = activity.get("feature", {})
    loc = activity.get("loc", {})
    branch = activity.get("branch", "unknown")
    is_significant = activity.get("is_significant", False)

    # Generate feature name from commit
    feature_title = "general-changes"
    if feature:
        feature_title = feature.get("title", "unknown-feature")
        # Sanitize for filename
        feature_title = re.sub(r"[^\w\s-]", "", feature_title)
        feature_title = re.sub(r"[-\s]+", "-", feature_title).lower()

    # Check if this should create a new feature page
    if is_significant or feature:
        feature_file = features_path / f"{feature_title}.md"

        # Build feature content with summary at top
        feature_content = f"""# {feature.get('title', feature_title).title()}

> **Summary:** {feature.get('title', 'Feature implementation')} - {loc.get('total_changes', 0)} lines changed
> **Branch:** `{branch}`
> **Date:** {activity['timestamp']}

---

## Overview

{f'**Type:** {feature.get("type", "implementation").title()}' if feature else ''}
**Files Changed:** {len(activity.get('changes', []))}
**Lines Added:** +{loc.get('total_added', 0)}
**Lines Deleted:** -{loc.get('total_deleted', 0)}

## Changes

"""

        # Add file changes
        for fc in loc.get("files", []):
            if fc["added"] > 0 or fc["deleted"] > 0:
                feature_content += f"- `{fc['file']}`: +{fc['added']} / -{fc['deleted']}\n"

        # Add commit details
        commit = activity.get("commit", {})
        if commit.get("subject"):
            feature_content += f"\n## Commit\n\n**{commit['subject']}**\n"
            if commit.get("body"):
                feature_content += f"\n{commit['body']}\n"

        # Add all changes
        categories = activity.get("categories", {})
        if categories.get("added"):
            feature_content += "\n### Added Files\n"
            for f in categories["added"]:
                feature_content += f"- `{f}`\n"

        if categories.get("modified"):
            feature_content += "\n### Modified Files\n"
            for f in categories["modified"]:
                feature_content += f"- `{f}`\n"

        if categories.get("deleted"):
            feature_content += "\n### Deleted Files\n"
            for f in categories["deleted"]:
                feature_content += f"- `{f}`\n"

        feature_content += f"\n---\n*Generated by SchemaWiki on {datetime.now().isoformat()}*\n"

        # Write feature file
        feature_file.write_text(feature_content)
        print(f"Created/Updated: {feature_file}")

        # Update README with link
        readme_content = generate_readme_links(features_path)
    else:
        # Small change - just update general readme
        readme_content = generate_readme_links(features_path)

    # Update main README
    readme.write_text(readme_content)
    print(f"Updated: {readme}")
    return readme


def generate_readme_links(features_path: Path) -> str:
    """Generate README with links to all feature pages."""
    # Get all feature files
    feature_files = sorted(features_path.glob("*.md"))

    features_list = []
    for f in feature_files:
        # Try to extract summary from first line
        content = f.read_text()
        lines = content.split("\n")
        title = f.stem.replace("-", " ").title()
        summary = ""
        for line in lines:
            if line.startswith("> **Summary:**"):
                summary = line.replace("> **Summary:**", "").strip()
                break

        features_list.append({"file": f"features/{f.name}", "title": title, "summary": summary})

    # Build README
    readme = f"""# Project Wiki

Generated by SchemaWiki
**Last Updated:** {datetime.now().isoformat()}

---

## Project Overview

This wiki documents all significant features and changes to the project.

"""

    if features_list:
        readme += "## Features & Changes\n\n"
        for feat in features_list:
            readme += f"### [{feat['title']}]({feat['file']})\n"
            if feat["summary"]:
                readme += f"> {feat['summary']}\n"
            readme += "\n"
    else:
        readme += "## Recent Changes\n\nNo significant changes detected yet.\n"

    readme += f"\n---\n*Auto-generated by SchemaWiki*\n"

    return readme


def deploy_to_github_pages(branch: str = "gh-pages"):
    """Deploy wiki to GitHub Pages."""
    import subprocess
    import urllib.parse

    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPO")

    if not token:
        print("Error: GITHUB_TOKEN not set")
        return False

    # Check if there are changes
    result = subprocess.run(
        ["git", "status", "--porcelain", f"{WIKI_DIR}/"],
        capture_output=True,
        text=True,
    )

    if not result.stdout.strip():
        print("No wiki changes to deploy")
        return True

    print(f"Deploying to GitHub Pages...\n{result.stdout}")

    # Configure git
    subprocess.run(
        ["git", "config", "--local", "user.email", "schemawiki[bot]@users.noreply.github.com"],
        check=False,
    )
    subprocess.run(["git", "config", "--local", "user.name", "SchemaWiki Bot"], check=False)

    # Get remote URL
    remote_result = subprocess.run(
        ["git", "remote", "get-url", "origin"], capture_output=True, text=True, check=True
    )
    remote_url = remote_result.stdout.strip()

    # Create auth URL
    if "github.com" in remote_url:
        parsed = urllib.parse.urlparse(remote_url)
        auth_url = f"https://x-access-token:{token}@{parsed.netloc}{parsed.path}"
    else:
        print("Not a GitHub repository")
        return False

    # Check if gh-pages branch exists
    check_branch = subprocess.run(
        ["git", "ls-remote", "--heads", auth_url, branch],
        capture_output=True,
        text=True,
    )

    if check_branch.returncode == 0 and check_branch.stdout.strip():
        # Branch exists, checkout and update
        subprocess.run(["git", "fetch", auth_url, branch], check=False)
        subprocess.run(
            ["git", "checkout", "-b", branch, f"origin/{branch}"],
            capture_output=True,
            check=False,
        )
    else:
        # Create new branch
        subprocess.run(["git", "checkout", "--orphan", branch], check=False)

    # Copy wiki files to root (GitHub Pages serves from root)
    import shutil

    wiki_path = Path(WIKI_DIR)
    docs_path = Path("docs")
    docs_path.mkdir(exist_ok=True)

    # Copy all wiki files to docs/
    for f in wiki_path.glob("*.md"):
        shutil.copy(f, docs_path / f.name)

    # Create index.html redirect if needed
    index_html = docs_path / "index.html"
    if not index_html.exists():
        index_html.write_text("""<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="refresh" content="0; URL=README.html">
    <title>Redirecting to Wiki...</title>
</head>
<body>
    <p>Redirecting to <a href="README.html">Wiki</a>...</p>
</body>
</html>""")

    # Commit and push
    subprocess.run(["git", "add", "-A"], check=True)
    subprocess.run(
        ["git", "commit", "-m", f"docs: Update SchemaWiki {datetime.now().isoformat()}"],
        check=False,
    )

    # Push
    push_result = subprocess.run(
        ["git", "push", auth_url, f"{branch}:{branch}", "--force"],
        capture_output=True,
        text=True,
    )

    # Switch back to original branch
    subprocess.run(["git", "checkout", "-"], check=False)

    if push_result.returncode == 0:
        print(f"\nDeployed to GitHub Pages!")
        print(f"Enable at: Repo Settings → Pages → Source: {branch} branch")
        return True
    else:
        print(f"Push failed: {push_result.stderr}")
        return False


def show_analysis():
    """Show analysis without updating wiki."""
    activity = analyze_ai_activity()

    print("\n=== SchemaWiki Analysis ===\n")
    print(f"Branch: {activity['branch']}")
    print(f"Timestamp: {activity['timestamp']}")
    print(f"\nLast Commit: {activity['commit'].get('subject', 'N/A')}")

    feature = activity.get("feature")
    if feature:
        print(f"\nDetected: {feature['type']} - {feature['title']}")

    # LOC Analysis
    loc = activity.get("loc", {})
    print(f"\n--- LOC Analysis ---")
    print(f"Lines Added: +{loc.get('total_added', 0)}")
    print(f"Lines Deleted: -{loc.get('total_deleted', 0)}")
    print(f"Total Changes: {loc.get('total_changes', 0)}")

    # Check significance
    is_sig = activity.get("is_significant", False)
    print(
        f"\n*** SIGNIFICANT CHANGE: {'YES - Will create feature page' if is_sig else 'NO - Will not create new page'} ***"
    )
    print(f"(Threshold: {LOC_THRESHOLD}+ LOC or 5+ files)")

    categories = activity.get("categories", {})
    print(f"\n--- File Changes ---")
    print(f"  Added: {len(categories.get('added', []))}")
    print(f"  Modified: {len(categories.get('modified', []))}")
    print(f"  Deleted: {len(categories.get('deleted', []))}")

    if categories.get("added"):
        print("\nAdded files:")
        for f in categories["added"][:5]:
            print(f"  + {f}")
        if len(categories["added"]) > 5:
            print(f"  ... and {len(categories['added']) - 5} more")

    if categories.get("modified"):
        print("\nModified files:")
        for f in categories["modified"][:5]:
            print(f"  M {f}")
        if len(categories["modified"]) > 5:
            print(f"  ... and {len(categories['modified']) - 5} more")

    print()
    return activity


def main():
    parser = argparse.ArgumentParser(
        description="SchemaWiki Analyzer - AI session tracking for any project"
    )
    parser.add_argument(
        "--analyze", "-a", action="store_true", help="Analyze without updating wiki"
    )
    parser.add_argument("--update", "-u", action="store_true", help="Update wiki with new activity")
    parser.add_argument(
        "--branch", "-b", default="origin/main", help="Base branch to compare against"
    )
    parser.add_argument("--output", "-o", help="Output file for wiki update")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument(
        "--github-pages",
        "-g",
        action="store_true",
        help="Deploy to GitHub Pages (requires GITHUB_TOKEN)",
    )
    parser.add_argument(
        "--pages-branch",
        default="gh-pages",
        help="Branch for GitHub Pages deployment",
    )

    args = parser.parse_args()

    # Analyze activity
    activity = analyze_ai_activity()

    if args.json:
        import json

        print(json.dumps(activity, indent=2))
        return

    if args.analyze:
        show_analysis()
    elif args.update:
        update_wiki(activity)
        if args.github_pages:
            deploy_to_github_pages(branch=args.pages_branch)
    else:
        # Default: analyze and show
        show_analysis()
        update_wiki(activity)


if __name__ == "__main__":
    main()
