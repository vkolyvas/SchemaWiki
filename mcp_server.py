"""SchemaWiki MCP Server - Record AI agent activities with rich context."""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import uvicorn
from fastapi import FastAPI, HTTPException

# MCP imports
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from pydantic import BaseModel

app = FastAPI(title="SchemaWiki MCP Server")

# Store for in-memory feature data
FEATURES: dict[str, dict] = {}

# Wiki data path - where wikis are saved
WIKI_DATA_PATH = os.environ.get("WIKI_DATA_PATH", "/data/wikis")
Path(WIKI_DATA_PATH).mkdir(parents=True, exist_ok=True)

# Project configuration
PROJECT_NAME = os.environ.get("PROJECT_NAME", "SchemaWiki")
PROJECT_URL = os.environ.get("PROJECT_URL", "")
PROJECT_GITHUB_URL = os.environ.get("PROJECT_GITHUB_URL", "")

# GitHub repository for wiki uploads (optional)
GITHUB_REPO = os.environ.get("GITHUB_REPO", "")  # e.g., "owner/repo"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")  # GitHub token for pushing
WIKI_BRANCH = os.environ.get("WIKI_BRANCH", "main")


class FeatureRecord(BaseModel):
    name: str
    description: Optional[str] = None
    version: str = "0.1.0"
    tags: list[str] = []
    plan_content: Optional[str] = None


class StepRecord(BaseModel):
    feature_name: str
    step: str
    why: Optional[str] = None  # Why this step was taken
    trigger: Optional[str] = (
        None  # What triggered this (e.g., "user_request", "error", "test_failure")
    )
    command: Optional[str] = None
    files_modified: list[str] = []
    output: Optional[str] = None
    status: str = "in_progress"
    context: Optional[str] = None  # Additional context


class EventRecord(BaseModel):
    feature_name: str
    event_type: str  # feature_coded, service_restarted, change_pushed, missing_code, lint_error, test_passed, test_failed, bug_fix, code_review, refactor
    why: str  # Why this happened
    details: Optional[str] = None
    files: list[str] = []


# MCP Server Setup
server = Server("schemawiki")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="create_feature",
            description="Create a new feature record in SchemaWiki",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Feature name"},
                    "description": {"type": "string", "description": "Feature description"},
                    "version": {"type": "string", "description": "Semantic version"},
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Feature tags",
                    },
                    "plan": {"type": "string", "description": "Initial plan content"},
                    "why": {"type": "string", "description": "Why this feature is being built"},
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="record_step",
            description="Record an implementation step with reasoning",
            inputSchema={
                "type": "object",
                "properties": {
                    "feature_name": {"type": "string", "description": "Feature name"},
                    "step": {"type": "string", "description": "Description of the step"},
                    "why": {"type": "string", "description": "Why this step was taken"},
                    "trigger": {
                        "type": "string",
                        "description": "What triggered this (user_request, error, test_failure, lint_error, missing_code, bug_fix)",
                    },
                    "command": {"type": "string", "description": "Command executed"},
                    "files_modified": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Files modified",
                    },
                    "output": {"type": "string", "description": "Command output"},
                    "status": {
                        "type": "string",
                        "enum": ["in_progress", "completed", "failed"],
                        "description": "Step status",
                    },
                    "context": {"type": "string", "description": "Additional context"},
                },
                "required": ["feature_name", "step", "why"],
            },
        ),
        Tool(
            name="record_event",
            description="Record a development event (restart, push, test, etc.) with reasoning",
            inputSchema={
                "type": "object",
                "properties": {
                    "feature_name": {"type": "string", "description": "Feature name"},
                    "event_type": {
                        "type": "string",
                        "enum": [
                            "feature_coded",
                            "service_restarted",
                            "change_pushed",
                            "missing_code",
                            "lint_error",
                            "test_passed",
                            "test_failed",
                            "bug_fix",
                            "code_review",
                            "refactor",
                            "dependency_added",
                            "config_changed",
                            "api_contract_change",
                            "db_migration",
                        ],
                        "description": "Type of event",
                    },
                    "why": {"type": "string", "description": "Why this happened"},
                    "details": {"type": "string", "description": "Event details"},
                    "files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Related files",
                    },
                    "auto_wiki": {
                        "type": "boolean",
                        "description": "Auto-generate and push wiki after this event (if GITHUB_REPO set)",
                    },
                },
                "required": ["feature_name", "event_type", "why"],
            },
        ),
        Tool(
            name="update_implementation",
            description="Update the implementation documentation",
            inputSchema={
                "type": "object",
                "properties": {
                    "feature_name": {"type": "string", "description": "Feature name"},
                    "content": {"type": "string", "description": "Implementation content"},
                    "why": {"type": "string", "description": "Why this was added"},
                },
                "required": ["feature_name", "content"],
            },
        ),
        Tool(
            name="add_debug_log",
            description="Add a debug log with error analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "feature_name": {"type": "string", "description": "Feature name"},
                    "attempt": {"type": "integer", "description": "Attempt number"},
                    "error": {"type": "string", "description": "Error message"},
                    "why_failed": {
                        "type": "string",
                        "description": "Why it failed (root cause analysis)",
                    },
                    "fix_applied": {"type": "string", "description": "Fix that was applied"},
                    "log": {"type": "string", "description": "Debug log content"},
                },
                "required": ["feature_name", "attempt", "error"],
            },
        ),
        Tool(
            name="get_feature",
            description="Get full feature details",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Feature name"},
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="generate_wiki",
            description="Generate a wiki page for a feature",
            inputSchema={
                "type": "object",
                "properties": {
                    "feature_name": {"type": "string", "description": "Feature name"},
                    "format": {
                        "type": "string",
                        "enum": ["markdown", "html"],
                        "description": "Output format",
                    },
                    "push_to_github": {
                        "type": "boolean",
                        "description": "Push wiki to GitHub repo (requires GITHUB_REPO and GITHUB_TOKEN env vars)",
                    },
                },
                "required": ["feature_name"],
            },
        ),
        Tool(
            name="list_features",
            description="List all recorded features",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="search_features",
            description="Search features by query",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                },
                "required": ["query"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    if name == "create_feature":
        return await create_feature(arguments)
    elif name == "record_step":
        return await record_step(arguments)
    elif name == "record_event":
        return await record_event(arguments)
    elif name == "update_implementation":
        return await update_implementation(arguments)
    elif name == "add_debug_log":
        return await add_debug_log(arguments)
    elif name == "get_feature":
        return await get_feature(arguments)
    elif name == "generate_wiki":
        return await generate_wiki(arguments)
    elif name == "list_features":
        return await list_features()
    elif name == "search_features":
        return await search_features(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")


async def create_feature(args: dict) -> list[TextContent]:
    """Create a new feature."""
    name = args.get("name")
    if not name:
        raise ValueError("Feature name is required")

    feature = {
        "name": name,
        "description": args.get("description", ""),
        "version": args.get("version", "0.1.0"),
        "tags": args.get("tags", []),
        "status": "planning",
        "why": args.get("why", ""),  # Why this feature exists
        "plan": args.get("plan", ""),
        "implementation": "",
        "steps": [],
        "events": [],
        "debug_logs": [],
        "created_at": datetime.utcnow().isoformat(),
    }

    FEATURES[name] = feature

    return [
        TextContent(type="text", text=json.dumps({"status": "created", "feature": name}, indent=2))
    ]


async def record_step(args: dict) -> list[TextContent]:
    """Record an implementation step with reasoning."""
    feature_name = args.get("feature_name")
    if not feature_name or feature_name not in FEATURES:
        raise ValueError(f"Feature '{feature_name}' not found")

    step = {
        "step": args.get("step", ""),
        "why": args.get("why", ""),  # Why this step was taken
        "trigger": args.get("trigger", ""),  # What triggered this
        "command": args.get("command", ""),
        "files_modified": args.get("files_modified", []),
        "output": args.get("output", ""),
        "status": args.get("status", "in_progress"),
        "context": args.get("context", ""),
        "timestamp": datetime.utcnow().isoformat(),
    }

    FEATURES[feature_name]["steps"].append(step)

    # Update status
    if args.get("status") == "completed":
        FEATURES[feature_name]["status"] = "in_progress"
    elif args.get("status") == "failed":
        FEATURES[feature_name]["status"] = "failed"

    return [
        TextContent(
            type="text",
            text=json.dumps(
                {"status": "recorded", "step": len(FEATURES[feature_name]["steps"])}, indent=2
            ),
        )
    ]


async def record_event(args: dict) -> list[TextContent]:
    """Record a development event."""
    feature_name = args.get("feature_name")
    if not feature_name or feature_name not in FEATURES:
        raise ValueError(f"Feature '{feature_name}' not found")

    event = {
        "event_type": args.get("event_type", ""),
        "why": args.get("why", ""),  # Why this happened
        "details": args.get("details", ""),
        "files": args.get("files", []),
        "timestamp": datetime.utcnow().isoformat(),
    }

    FEATURES[feature_name]["events"].append(event)

    # Auto-generate wiki on these events
    auto_wiki_events = ["feature_coded", "change_pushed", "service_restarted"]
    auto_push = args.get("auto_wiki", False) or GITHUB_REPO

    if args.get("event_type") in auto_wiki_events and auto_push:
        try:
            wiki = generate_markdown_wiki(FEATURES[feature_name])
            filename = f"{feature_name}.md"
            wiki_path = Path(WIKI_DATA_PATH) / filename
            wiki_path.write_text(wiki)
            FEATURES[feature_name]["wiki_path"] = str(wiki_path)

            # Push to GitHub if configured
            if GITHUB_REPO and GITHUB_TOKEN:
                github_url = await push_wiki_to_github(feature_name, wiki, "markdown")
                FEATURES[feature_name]["github_wiki_url"] = github_url
        except Exception as e:
            pass  # Don't fail the event recording

    return [
        TextContent(
            type="text",
            text=json.dumps({"status": "recorded", "event": args.get("event_type")}, indent=2),
        )
    ]


async def update_implementation(args: dict) -> list[TextContent]:
    """Update implementation documentation."""
    feature_name = args.get("feature_name")
    if not feature_name or feature_name not in FEATURES:
        raise ValueError(f"Feature '{feature_name}' not found")

    content = args.get("content", "")
    why = args.get("why", "")

    entry = f"\n\n## {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
    if why:
        entry += f"\n**Why:** {why}"
    entry += f"\n\n{content}"

    FEATURES[feature_name]["implementation"] += entry

    return [
        TextContent(
            type="text", text=json.dumps({"status": "updated", "feature": feature_name}, indent=2)
        )
    ]


async def add_debug_log(args: dict) -> list[TextContent]:
    """Add a debug log with root cause analysis."""
    feature_name = args.get("feature_name")
    if not feature_name or feature_name not in FEATURES:
        raise ValueError(f"Feature '{feature_name}' not found")

    log_entry = {
        "attempt": args.get("attempt", 1),
        "error": args.get("error", ""),
        "why_failed": args.get("why_failed", ""),  # Root cause
        "fix_applied": args.get("fix_applied", ""),  # What was done to fix
        "log": args.get("log", ""),
        "timestamp": datetime.utcnow().isoformat(),
    }

    FEATURES[feature_name]["debug_logs"].append(log_entry)

    return [
        TextContent(
            type="text",
            text=json.dumps({"status": "logged", "attempt": log_entry["attempt"]}, indent=2),
        )
    ]


async def get_feature(args: dict) -> list[TextContent]:
    """Get feature details."""
    name = args.get("name")
    if not name or name not in FEATURES:
        raise ValueError(f"Feature '{name}' not found")

    return [TextContent(type="text", text=json.dumps(FEATURES[name], indent=2))]


async def generate_wiki(args: dict) -> list[TextContent]:
    """Generate wiki page for a feature."""
    feature_name = args.get("feature_name")
    if not feature_name or feature_name not in FEATURES:
        raise ValueError(f"Feature '{feature_name}' not found")

    feature = FEATURES[feature_name]
    fmt = args.get("format", "markdown")
    push_to_github = args.get("push_to_github", False)

    if fmt == "html":
        wiki = generate_html_wiki(feature)
        filename = f"{feature_name}.html"
    else:
        wiki = generate_markdown_wiki(feature)
        filename = f"{feature_name}.md"

    # Save wiki to disk
    wiki_path = Path(WIKI_DATA_PATH) / filename
    wiki_path.write_text(wiki)

    # Also save to feature for reference
    feature["wiki_path"] = str(wiki_path)
    feature["wiki_format"] = fmt

    # Optionally push to GitHub
    if push_to_github or GITHUB_REPO:
        github_path = await push_wiki_to_github(feature_name, wiki, fmt)
        feature["github_wiki_url"] = github_path

    return [TextContent(type="text", text=wiki)]


async def push_wiki_to_github(feature_name: str, content: str, fmt: str) -> str:
    """Push wiki file to GitHub repository."""
    if not GITHUB_REPO or not GITHUB_TOKEN:
        raise ValueError("GITHUB_REPO and GITHUB_TOKEN must be set to push to GitHub")

    import httpx

    branch = WIKI_BRANCH
    filename = f"SchemaWiki/{feature_name}.{'md' if fmt == 'markdown' else 'html'}"

    # Get the current file SHA if it exists (for updates)
    sha = None
    async with httpx.AsyncClient() as client:
        # Try to get existing file
        get_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{filename}"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
        }
        resp = await client.get(get_url, headers=headers)
        if resp.status_code == 200:
            sha = resp.json().get("sha")

        # Create or update file
        data = {
            "message": f"Update wiki: {feature_name}",
            "content": content.encode("utf-8").decode("latin-1"),
            "branch": branch,
        }
        if sha:
            data["sha"] = sha

        put_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{filename}"
        resp = await client.put(put_url, json=data, headers=headers)

        if resp.status_code not in (200, 201):
            raise ValueError(f"GitHub push failed: {resp.text}")

        return resp.json().get("content", {}).get("html_url", "")


def generate_markdown_wiki(feature: dict) -> str:
    """Generate Markdown wiki page with rich context."""
    lines = [
        f"**[{PROJECT_NAME}](/)** ",
        "",
        f"# {feature['name']}",
        "",
        f"**Version:** {feature['version']} ",
        f"**Status:** {feature['status']} ",
        f"**Created:** {feature.get('created_at', 'N/A')}",
        "",
    ]

    # WHY this feature exists
    if feature.get("why"):
        lines.extend(
            [
                "## Why This Feature Exists",
                "",
                feature["why"],
                "",
            ]
        )

    if feature.get("description"):
        lines.extend(
            [
                "## Description",
                "",
                feature.get("description", "No description provided."),
                "",
            ]
        )

    if feature.get("tags"):
        lines.extend(
            [
                "## Tags",
                "",
                ", ".join(f"`{tag}`" for tag in feature["tags"]),
                "",
            ]
        )

    if feature.get("plan"):
        lines.extend(
            [
                "## Plan",
                "",
                feature["plan"],
                "",
            ]
        )

    if feature.get("implementation"):
        lines.extend(
            [
                "## Implementation",
                "",
                feature["implementation"],
                "",
            ]
        )

    # EVENTS - Major things that happened
    if feature.get("events"):
        lines.append("## Development Events")
        lines.append("")
        for event in feature["events"]:
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
                "api_contract_change": "🔗",
                "db_migration": "🗄️",
                "feature_coded": "💻",
            }.get(event["event_type"], "📝")

            lines.append(f"### {event_emoji} {event['event_type'].replace('_', ' ').title()}")
            lines.append("")
            lines.append(f"**Why:** {event.get('why', 'N/A')}")
            if event.get("details"):
                lines.append("")
                lines.append(f"**Details:** {event['details']}")
            if event.get("files"):
                lines.append("")
                lines.append("**Files:**")
                for f in event["files"]:
                    lines.append(f"- `{f}`")
            lines.append("")

    # IMPLEMENTATION STEPS with WHY
    if feature.get("steps"):
        lines.append("## Implementation Steps")
        lines.append("")
        for i, step in enumerate(feature["steps"], 1):
            lines.append(f"### Step {i}: {step['step']}")
            lines.append("")

            # WHY this step was taken
            if step.get("why"):
                lines.append(f"> **Why:** {step['why']}")

            # Trigger
            if step.get("trigger"):
                lines.append(f"> **Trigger:** {step['trigger']}")

            # Command
            if step.get("command"):
                lines.append("")
                lines.append("```bash")
                lines.append(step["command"])
                lines.append("```")

            # Files modified
            if step.get("files_modified"):
                lines.append("")
                lines.append("**Files modified:**")
                for f in step["files_modified"]:
                    lines.append(f"- `{f}`")

            # Context
            if step.get("context"):
                lines.append("")
                lines.append(f"**Context:** {step['context']}")

            # Output (truncated)
            if step.get("output"):
                lines.append("")
                lines.append("**Output:**")
                lines.append("```")
                lines.append(step["output"][:500])
                lines.append("```")

            lines.append("")
            lines.append(f"**Status:** {step.get('status', 'unknown')}")
            lines.append("")

    # DEBUG LOGS with root cause analysis
    if feature.get("debug_logs"):
        lines.extend(
            [
                "## Debug Logs & Root Cause Analysis",
                "",
            ]
        )
        for log in feature["debug_logs"]:
            lines.append(f"### Attempt {log['attempt']}")
            lines.append("")
            lines.append(f"**Error:** `{log.get('error', 'N/A')}`")

            # WHY it failed
            if log.get("why_failed"):
                lines.append("")
                lines.append(f"**Why it failed:** {log['why_failed']}")

            # What was done to fix
            if log.get("fix_applied"):
                lines.append("")
                lines.append(f"**Fix applied:** {log['fix_applied']}")

            # Full log
            if log.get("log"):
                lines.append("")
                lines.append("**Debug log:**")
                lines.append("```")
                lines.append(log["log"])
                lines.append("```")
            lines.append("")

    return "\n".join(lines)


def generate_html_wiki(feature: dict) -> str:
    """Generate HTML wiki page."""
    md = generate_markdown_wiki(feature)
    # Simple conversion
    html = md.replace("# ", "<h1>").replace("\n## ", "</h1>\n<h2>").replace("\n### ", "</h2>\n<h3>")
    html = html.replace("**", "<strong>").replace("`", "<code>").replace(">", "<blockquote>")
    html = html.replace("\n\n", "</p>\n<p>")
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>{feature['name']} - SchemaWiki</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; line-height: 1.6; }}
        h1, h2, h3 {{ color: #1a1a1a; margin-top: 30px; }}
        code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
        pre {{ background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }}
        blockquote {{ border-left: 4px solid #0066cc; margin: 10px 0; padding-left: 15px; color: #555; }}
    </style>
</head>
<body>
{html}
</body>
</html>"""


async def list_features() -> list[TextContent]:
    """List all features."""
    return [TextContent(type="text", text=json.dumps(list(FEATURES.keys()), indent=2))]


async def search_features(args: dict) -> list[TextContent]:
    """Search features."""
    query = args.get("query", "").lower()
    results = []

    for name, feature in FEATURES.items():
        if query in name.lower() or query in feature.get("description", "").lower():
            results.append(feature)

    return [TextContent(type="text", text=json.dumps(results, indent=2))]


# REST API endpoints
@app.post("/features")
async def create_feature_api(feature: FeatureRecord):
    """REST API: Create feature."""
    args = feature.model_dump()
    result = await create_feature(args)
    return json.loads(result[0].text)


@app.get("/features")
async def list_features_api():
    """REST API: List all features."""
    features = []
    for name, data in FEATURES.items():
        features.append({"name": name, **data})
    return features


@app.post("/steps")
async def record_step_api(step: StepRecord):
    """REST API: Record step."""
    args = step.model_dump()
    result = await record_step(args)
    return json.loads(result[0].text)


@app.post("/events")
async def record_event_api(event: EventRecord):
    """REST API: Record event."""
    args = event.model_dump()
    result = await record_event(args)
    return json.loads(result[0].text)


@app.get("/features/{name}")
async def get_feature_api(name: str):
    """REST API: Get feature."""
    result = await get_feature({"name": name})
    return json.loads(result[0].text)


@app.get("/wiki/{name}")
async def generate_wiki_api(name: str, format: str = "markdown"):
    """REST API: Generate wiki."""
    result = await generate_wiki({"feature_name": name, "format": format})
    return result[0].text


@app.get("/wiki/{name}/view")
async def view_wiki_html(name: str):
    """View wiki as rendered HTML page."""
    from fastapi.responses import HTMLResponse

    # Get markdown wiki
    result = await generate_wiki({"feature_name": name, "format": "markdown"})
    md_content = result[0].text

    # Simple markdown to HTML conversion
    html_content = md_to_html(md_content)

    # Wrap in HTML page
    html_page = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{name} - SchemaWiki</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
        }}
        h1 {{ color: #1a1a1a; border-bottom: 2px solid #0066cc; padding-bottom: 10px; }}
        h2 {{ color: #2a2a2a; margin-top: 30px; }}
        h3 {{ color: #3a3a3a; }}
        code {{
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Monaco', 'Menlo', monospace;
        }}
        pre {{
            background: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        blockquote {{
            border-left: 4px solid #0066cc;
            margin: 10px 0;
            padding-left: 15px;
            color: #555;
            background: #f9f9f9;
        }}
        ul, ol {{ padding-left: 25px; }}
        li {{ margin: 5px 0; }}
        strong {{ color: #0066cc; }}
        hr {{ border: none; border-top: 1px solid #ddd; margin: 30px 0; }}
        .meta {{ color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""

    return HTMLResponse(html_page)


def md_to_html(md: str) -> str:
    """Simple markdown to HTML conversion."""
    import re

    html = md

    # Headers
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

    # Bold
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)

    # Code blocks
    html = re.sub(r'```(\w*)\n(.*?)```', r'<pre><code>\2</code></pre>', html, flags=re.DOTALL)

    # Inline code
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)

    # Lists
    html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'^(\d+)\. (.+)$', r'<li>\2</li>', html, flags=re.MULTILINE)

    # Wrap consecutive li in ul
    html = re.sub(r'(<li>.*?</li>\n?)+', r'<ul>\g<0></ul>', html)

    # Blockquotes
    html = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)

    # Paragraphs
    html = re.sub(r'\n\n+', '\n', html)
    lines = html.split('\n')
    result = []
    in_pre = False
    in_ul = False
    in_blockquote = False

    for line in lines:
        line = line.strip()
        if not line:
            if in_pre or in_ul or in_blockquote:
                if in_pre:
                    result.append('</code></pre>')
                    in_pre = False
                if in_ul:
                    result.append('</ul>')
                    in_ul = False
                if in_blockquote:
                    result.append('</blockquote>')
                    in_blockquote = False
            continue

        if line.startswith('<pre>') or line.startswith('<ul>') or line.startswith('<blockquote>'):
            result.append(line)
            continue
        if '</pre>' in line or '</ul>' in line or '</blockquote>' in line:
            result.append(line)
            continue

        if not line.startswith('<') and not line.startswith('#'):
            line = f'<p>{line}</p>'

        result.append(line)

    return '\n'.join(result)


@app.get("/wikis")
async def list_wikis():
    """List all saved wiki pages."""
    wikis = []
    for f in Path(WIKI_DATA_PATH).iterdir():
        if f.is_file():
            wikis.append(
                {
                    "name": f.stem,
                    "format": f.suffix[1],
                    "path": str(f),
                    "size": f.stat().st_size,
                    "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                }
            )
    return {"wikis": wikis}


@app.get("/wikis/{name}")
async def get_wiki(name: str):
    """Get a saved wiki page."""
    # Try markdown first, then html
    md_path = Path(WIKI_DATA_PATH) / f"{name}.md"
    html_path = Path(WIKI_DATA_PATH) / f"{name}.html"

    if md_path.exists():
        return {"name": name, "format": "markdown", "content": md_path.read_text()}
    elif html_path.exists():
        return {"name": name, "format": "html", "content": html_path.read_text()}
    else:
        raise HTTPException(status_code=404, detail="Wiki not found")


@app.get("/wikis/{name}/download")
async def download_wiki(name: str, format: str = "markdown"):
    """Download a wiki page file."""
    if format == "html":
        filename = f"{name}.html"
    else:
        filename = f"{name}.md"

    path = Path(WIKI_DATA_PATH) / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Wiki not found")

    from fastapi.responses import FileResponse

    return FileResponse(path, filename=filename)


@app.get("/health")
async def health():
    return {"status": "healthy", "wiki_path": WIKI_DATA_PATH, "project": PROJECT_NAME}


def generate_project_wiki() -> str:
    """Generate project index wiki page."""
    lines = [
        f"# {PROJECT_NAME}",
        "",
        f"**Total Features:** {len(FEATURES)}",
        "",
    ]

    if PROJECT_URL:
        lines.append(f"**Website:** [{PROJECT_URL}]({PROJECT_URL})")
        lines.append("")

    if PROJECT_GITHUB_URL:
        lines.append(f"**GitHub:** [{PROJECT_GITHUB_URL}]({PROJECT_GITHUB_URL})")
        lines.append("")

    lines.extend([
        "## All Features",
        "",
    ])

    for name, feature in FEATURES.items():
        why = feature.get("why", "No description")
        why_short = why[:80] + "..." if len(why) > 80 else why
        lines.append(f"### [{name}](/wiki/{name})")
        lines.append(f"_{why_short}_")
        lines.append("")

    return "\n".join(lines)


@app.get("/")
async def project_index():
    """Project index page."""
    from fastapi.responses import HTMLResponse

    md = generate_project_wiki()
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{PROJECT_NAME} - SchemaWiki</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
        }}
        h1 {{ color: #1a1a1a; border-bottom: 2px solid #0066cc; padding-bottom: 10px; }}
        h2 {{ color: #2a2a2a; margin-top: 30px; }}
        h3 a {{ color: #0066cc; text-decoration: none; }}
        h3 a:hover {{ text-decoration: underline; }}
        code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
        pre {{ background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }}
        blockquote {{ border-left: 4px solid #0066cc; margin: 10px 0; padding-left: 15px; color: #555; }}
        ul, ol {{ padding-left: 25px; }}
        li {{ margin: 5px 0; }}
        strong {{ color: #0066cc; }}
        hr {{ border: none; border-top: 1px solid #ddd; margin: 30px 0; }}
        .nav {{ margin-bottom: 20px; }}
        .nav a {{ margin-right: 15px; color: #0066cc; }}
    </style>
</head>
<body>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/wikis">All Wikis</a>
    </div>
    {md_to_html(md)}
</body>
</html>"""
    return HTMLResponse(html)


async def main():
    """Run the MCP server."""
    import threading

    def run_api():
        uvicorn.run(app, host="0.0.0.0", port=8081, log_level="warning")

    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()

    # If REST_ONLY mode, just run the API without MCP stdio
    if os.environ.get("REST_ONLY", "").lower() == "true":
        print("Running in REST API only mode (no MCP stdio)")
        # Keep the main thread alive
        while True:
            await asyncio.sleep(3600)
    else:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            )


if __name__ == "__main__":
    asyncio.run(main())
