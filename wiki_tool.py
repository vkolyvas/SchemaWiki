#!/usr/bin/env python3
"""
SchemaWiki CLI - Direct markdown file-based feature documentation
Usage without MCP server - just read/write .md files directly
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Configuration
WIKI_DIR = Path(os.environ.get("SCHEMAWIKI_DIR", "SchemaWiki/features"))
WIKI_DIR.mkdir(parents=True, exist_ok=True)


def get_user_id() -> str:
    """Auto-detect user_id from environment."""
    env_vars = [
        "CLAUDE_SESSION_ID",
        "SESSION_ID",
        "XDG_SESSION_ID",
        "SSH_CONNECTION",
        "SSH_CLIENT",
        "USER",
        "USERNAME",
    ]
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            if var in ("SSH_CONNECTION", "SSH_CLIENT"):
                return value.split()[0]
            return value
    return "default"


def sanitize_filename(name: str) -> str:
    """Sanitize feature name for filename."""
    return name.replace(" ", "-").replace("/", "-").lower()


def create_feature(
    name: str, why: str, description: str = None, user_id: str = None, tags: list = None
):
    """Create a new feature markdown file."""
    user_id = user_id or get_user_id()
    filename = f"{sanitize_filename(name)}.md"
    filepath = WIKI_DIR / filename

    if filepath.exists():
        print(f"Feature '{name}' already exists at {filepath}")
        return filepath

    tags_str = ", ".join(f"`{t}`" for t in (tags or [])) or "None"

    content = f"""**[{WIKI_DIR.parent.name}](../)**

# {name}

**Version:** 0.1.0
**Status:** planning
**User:** {user_id}
**Created:** {datetime.now().isoformat()}
**Tags:** {tags_str}

## Why This Feature Exists

{why}

## Description

{description or 'No description provided.'}

## Plan



## Implementation



## Implementation Steps



## Development Events



## Debug Logs

"""
    filepath.write_text(content)
    print(f"Created: {filepath}")
    return filepath


def add_step(
    feature_name: str,
    step: str,
    why: str,
    trigger: str = None,
    command: str = None,
    files_modified: list = None,
    status: str = "in_progress",
):
    """Add a step to a feature."""
    filename = f"{sanitize_filename(feature_name)}.md"
    filepath = WIKI_DIR / filename

    if not filepath.exists():
        print(f"Feature '{feature_name}' not found")
        return None

    content = filepath.read_text()

    # Find the Implementation Steps section
    if "## Implementation Steps" in content:
        # Count existing steps
        step_count = content.count("### Step ")

        new_step = f"""
### Step {step_count + 1}: {step}

> **Why:** {why}
"""

        if trigger:
            new_step += f"> **Trigger:** {trigger}\n"

        if command:
            new_step += f"""
```bash
{command}
```
"""

        if files_modified:
            new_step += "\n**Files modified:**\n"
            for f in files_modified:
                new_step += f"- `{f}`\n"

        new_step += f"\n**Status:** {status}\n"

        # Insert after Implementation Steps header
        parts = content.split("## Implementation Steps")
        content = parts[0] + "## Implementation Steps" + new_step + parts[1]

    filepath.write_text(content)
    print(f"Added step to: {filepath}")
    return filepath


def add_event(
    feature_name: str, event_type: str, why: str, details: str = None, files: list = None
):
    """Add an event to a feature."""
    filename = f"{sanitize_filename(feature_name)}.md"
    filepath = WIKI_DIR / filename

    if not filepath.exists():
        print(f"Feature '{feature_name}' not found")
        return None

    content = filepath.read_text()

    event_emoji = {
        "service_restarted": "🔄",
        "change_pushed": "📤",
        "test_passed": "✅",
        "test_failed": "❌",
        "lint_error": "⚠️",
        "bug_fix": "🐛",
        "code_review": "👀",
        "refactor": "♻️",
        "dependency_added": "📦",
        "config_changed": "⚙️",
        "feature_coded": "💻",
    }.get(event_type, "📝")

    event_md = f"""
### {event_emoji} {event_type.replace('_', ' ').title()}

**Why:** {why}
"""

    if details:
        event_md += f"\n**Details:** {details}\n"

    if files:
        event_md += "\n**Files:**\n"
        for f in files:
            event_md += f"- `{f}`\n"

    # Insert into Development Events section
    if "## Development Events" in content:
        parts = content.split("## Development Events")
        content = parts[0] + "## Development Events" + event_md + parts[1]

    filepath.write_text(content)
    print(f"Added event to: {filepath}")
    return filepath


def add_implementation(feature_name: str, content_text: str, why: str = None):
    """Add implementation notes to a feature."""
    filename = f"{sanitize_filename(feature_name)}.md"
    filepath = WIKI_DIR / filename

    if not filepath.exists():
        print(f"Feature '{feature_name}' not found")
        return None

    content = filepath.read_text()

    impl = f"\n\n---\n**{datetime.now().strftime('%Y-%m-%d %H:%M')}**"
    if why:
        impl += f"\n**Why:** {why}"
    impl += f"\n\n{content_text}"

    # Find Implementation section
    if "## Implementation" in content:
        parts = content.split("## Implementation")
        content = parts[0] + "## Implementation" + impl + parts[1]

    filepath.write_text(content)
    print(f"Updated implementation: {filepath}")
    return filepath


def add_debug_log(
    feature_name: str,
    attempt: int,
    error: str,
    why_failed: str = None,
    fix_applied: str = None,
    log_text: str = None,
):
    """Add a debug log to a feature."""
    filename = f"{sanitize_filename(feature_name)}.md"
    filepath = WIKI_DIR / filename

    if not filepath.exists():
        print(f"Feature '{feature_name}' not found")
        return None

    content = filepath.read_text()

    debug = f"""
### Attempt {attempt}

**Error:** `{error}`
"""

    if why_failed:
        debug += f"\n**Why it failed:** {why_failed}\n"

    if fix_applied:
        debug += f"\n**Fix applied:** {fix_applied}\n"

    if log_text:
        debug += f"""
**Debug log:**
```
{log_text}
```
"""

    # Insert into Debug Logs section
    if "## Debug Logs" in content:
        parts = content.split("## Debug Logs")
        content = parts[0] + "## Debug Logs" + debug + parts[1]

    filepath.write_text(content)
    print(f"Added debug log to: {filepath}")
    return filepath


def list_features():
    """List all features."""
    features = sorted(WIKI_DIR.glob("*.md"))
    if not features:
        print("No features found")
        return

    print(f"\nFeatures in {WIKI_DIR}:\n")
    for f in features:
        name = f.stem
        # Try to get status from file
        content = f.read_text()
        status = "unknown"
        for line in content.split("\n"):
            if "**Status:**" in line:
                status = line.split("**Status:**")[1].strip()
                break
        print(f"  - {name} [{status}]")
    print()


def view_feature(name: str):
    """View a feature markdown file."""
    filename = f"{sanitize_filename(name)}.md"
    filepath = WIKI_DIR / filename

    if not filepath.exists():
        print(f"Feature '{name}' not found")
        return None

    print(filepath.read_text())
    return filepath


def generate_index():
    """Generate project index linking all features."""
    from collections import defaultdict

    users = defaultdict(list)
    features = sorted(WIKI_DIR.glob("*.md"))

    for f in features:
        content = f.read_text()
        user = "default"
        for line in content.split("\n"):
            if "**User:**" in line:
                user = line.split("**User:**")[1].strip()
                break
        users[user].append(f.stem)

    index = f"""# {WIKI_DIR.parent.name}

**Total Features:** {len(features)}
**Total Sessions:** {len(users)}

---

"""
    for user, feats in users.items():
        label = f"Session: {user}" if user != "default" else "Default"
        index += f"## {label}\n\n"
        for feat in feats:
            index += f"- [{feat}](features/{feat}.md)\n"
        index += "\n"

    index_path = WIKI_DIR.parent / "README.md"
    index_path.write_text(index)
    print(f"Generated index: {index_path}")
    return index_path


def main():
    parser = argparse.ArgumentParser(description="SchemaWiki CLI - Direct markdown file tool")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # create-feature
    subparsers.add_parser("create", help="Create a new feature")
    create_parser = subparsers.add_parser("create-feature", help="Create a new feature")
    create_parser.add_argument("name", help="Feature name")
    create_parser.add_argument("--why", required=True, help="Why this feature")
    create_parser.add_argument("--description", help="Feature description")
    create_parser.add_argument("--user-id", help="User/session ID")
    create_parser.add_argument("--tags", nargs="+", help="Tags")

    # step
    step_parser = subparsers.add_parser("step", help="Add a step")
    step_parser.add_argument("feature", help="Feature name")
    step_parser.add_argument("--step", required=True, help="Step description")
    step_parser.add_argument("--why", required=True, help="Why this step")
    step_parser.add_argument("--trigger", help="What triggered this")
    step_parser.add_argument("--cmd", help="Command executed")
    step_parser.add_argument("--files", nargs="+", help="Files modified")
    step_parser.add_argument("--status", default="in_progress", help="Step status")

    # event
    event_parser = subparsers.add_parser("event", help="Add an event")
    event_parser.add_argument("feature", help="Feature name")
    event_parser.add_argument("--type", required=True, help="Event type")
    event_parser.add_argument("--why", required=True, help="Why this happened")
    event_parser.add_argument("--details", help="Event details")
    event_parser.add_argument("--files", nargs="+", help="Related files")

    # implementation
    impl_parser = subparsers.add_parser("impl", help="Add implementation notes")
    impl_parser.add_argument("feature", help="Feature name")
    impl_parser.add_argument("--content", required=True, help="Implementation content")
    impl_parser.add_argument("--why", help="Why this was added")

    # debug
    debug_parser = subparsers.add_parser("debug", help="Add debug log")
    debug_parser.add_argument("feature", help="Feature name")
    debug_parser.add_argument("--attempt", type=int, default=1, help="Attempt number")
    debug_parser.add_argument("--error", required=True, help="Error message")
    debug_parser.add_argument("--why-failed", help="Why it failed")
    debug_parser.add_argument("--fix", help="Fix applied")
    debug_parser.add_argument("--log", help="Debug log content")

    # list
    subparsers.add_parser("list", help="List all features")

    # view
    view_parser = subparsers.add_parser("view", help="View a feature")
    view_parser.add_argument("name", help="Feature name")

    # index
    subparsers.add_parser("index", help="Generate project index")

    # push to github
    push_parser = subparsers.add_parser("push", help="Push wiki to GitHub")
    push_parser.add_argument("--message", default="Update SchemaWiki", help="Commit message")
    push_parser.add_argument("--repo", help="GitHub repo (owner/repo)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command in ("create", "create-feature"):
        create_feature(args.name, args.why, args.description, args.user_id, args.tags)
    elif args.command == "step":
        add_step(args.feature, args.step, args.why, args.trigger, args.cmd, args.files, args.status)
    elif args.command == "event":
        add_event(args.feature, args.type, args.why, args.details, args.files)
    elif args.command in ("impl", "implementation"):
        add_implementation(args.feature, args.content, args.why)
    elif args.command == "debug":
        add_debug_log(args.feature, args.attempt, args.error, args.why_failed, args.fix, args.log)
    elif args.command == "list":
        list_features()
    elif args.command == "view":
        view_feature(args.name)
    elif args.command == "index":
        generate_index()
    elif args.command == "push":
        push_to_github(args.message, args.repo)


def push_to_github(message: str = None, repo: str = None):
    """Push SchemaWiki folder to GitHub."""
    import subprocess
    import urllib.parse

    message = message or "Update SchemaWiki"
    token = os.environ.get("GITHUB_TOKEN")
    repo = repo or os.environ.get("GITHUB_REPO")

    if not token:
        print("Error: GITHUB_TOKEN not set")
        print("Set it with: export GITHUB_TOKEN=your_token")
        return

    if not repo:
        print("Error: GITHUB_REPO not set")
        print("Set it with: export GITHUB_REPO=owner/repo")
        return

    # Check if there are changes
    result = subprocess.run(
        ["git", "status", "--porcelain", "SchemaWiki/"], capture_output=True, text=True
    )

    if not result.stdout.strip():
        print("No changes to SchemaWiki folder")
        return

    print(f"Changes detected:\n{result.stdout}")

    # Configure git
    subprocess.run(["git", "config", "--local", "user.email", "wiki-tool@local"], check=False)
    subprocess.run(["git", "config", "--local", "user.name", "SchemaWiki Bot"], check=False)

    # Add and commit
    subprocess.run(["git", "add", "SchemaWiki/"], check=True)
    subprocess.run(["git", "commit", "-m", message], check=True)

    # Push using GitHub API with token
    remote_url = subprocess.run(
        ["git", "remote", "get-url", "origin"], capture_output=True, text=True, check=True
    ).stdout.strip()

    # Update remote URL with token
    if "github.com" in remote_url:
        parsed = urllib.parse.urlparse(remote_url)
        auth_remote = f"https://x-access-token:{token}@{parsed.netloc}{parsed.path}"
        subprocess.run(["git", "remote", "set-url", "origin", auth_remote], check=True)

        # Push
        result = subprocess.run(
            ["git", "push", "origin", "master:main"], capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"Pushed to https://github.com/{repo}/tree/main/SchemaWiki")
        else:
            print(f"Push failed: {result.stderr}")
    else:
        print("Not a GitHub remote, skipping push")


if __name__ == "__main__":
    main()
