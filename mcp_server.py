"""SchemaWiki MCP Server - Record AI agent activities and generate wiki pages."""

import os
import json
import asyncio
from pathlib import Path
from typing import Optional, Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# MCP imports
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from mcp.server.notification_options import NotificationOptions

app = FastAPI(title="SchemaWiki MCP Server")

# Store for in-memory feature data (for MCP server without full DB)
FEATURES: dict[str, dict] = {}


class FeatureRecord(BaseModel):
    name: str
    description: Optional[str] = None
    version: str = "0.1.0"
    tags: list[str] = []
    plan_content: Optional[str] = None


class StepRecord(BaseModel):
    feature_name: str
    step: str
    command: Optional[str] = None
    files_modified: list[str] = []
    output: Optional[str] = None
    status: str = "in_progress"  # in_progress, completed, failed


class WikiContent(BaseModel):
    feature_name: str
    format: str = "markdown"  # markdown, html


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
                    "version": {"type": "string", "description": "Semantic version (default: 0.1.0)"},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "Feature tags"},
                    "plan": {"type": "string", "description": "Initial plan content"},
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="record_step",
            description="Record an implementation step taken by the agent",
            inputSchema={
                "type": "object",
                "properties": {
                    "feature_name": {"type": "string", "description": "Feature name"},
                    "step": {"type": "string", "description": "Description of the step"},
                    "command": {"type": "string", "description": "Command executed"},
                    "files_modified": {"type": "array", "items": {"type": "string"}, "description": "Files modified"},
                    "output": {"type": "string", "description": "Command output"},
                    "status": {"type": "string", "enum": ["in_progress", "completed", "failed"], "description": "Step status"},
                },
                "required": ["feature_name", "step"],
            },
        ),
        Tool(
            name="update_implementation",
            description="Update the implementation documentation",
            inputSchema={
                "type": "object",
                "properties": {
                    "feature_name": {"type": "string", "description": "Feature name"},
                    "content": {"type": "string", "description": "Implementation content to add"},
                },
                "required": ["feature_name", "content"],
            },
        ),
        Tool(
            name="add_debug_log",
            description="Add a debug log entry for a failed attempt",
            inputSchema={
                "type": "object",
                "properties": {
                    "feature_name": {"type": "string", "description": "Feature name"},
                    "attempt": {"type": "integer", "description": "Attempt number"},
                    "error": {"type": "string", "description": "Error message"},
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
                    "format": {"type": "string", "enum": ["markdown", "html"], "description": "Output format"},
                },
                "required": ["feature_name"],
            },
        ),
        Tool(
            name="list_features",
            description="List all recorded features",
            inputSchema={
                "type": "object",
                "properties": {},
            },
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
        "plan": args.get("plan", ""),
        "implementation": "",
        "steps": [],
        "debug_logs": [],
    }

    FEATURES[name] = feature

    return [TextContent(
        type="text",
        text=json.dumps({"status": "created", "feature": name}, indent=2)
    )]


async def record_step(args: dict) -> list[TextContent]:
    """Record an implementation step."""
    feature_name = args.get("feature_name")
    if not feature_name or feature_name not in FEATURES:
        raise ValueError(f"Feature '{feature_name}' not found")

    step = {
        "step": args.get("step", ""),
        "command": args.get("command", ""),
        "files_modified": args.get("files_modified", []),
        "output": args.get("output", ""),
        "status": args.get("status", "in_progress"),
    }

    FEATURES[feature_name]["steps"].append(step)

    # Update status based on step
    if args.get("status") == "completed":
        FEATURES[feature_name]["status"] = "in_progress"
    elif args.get("status") == "failed":
        FEATURES[feature_name]["status"] = "failed"

    return [TextContent(
        type="text",
        text=json.dumps({"status": "recorded", "step": len(FEATURES[feature_name]["steps"])}, indent=2)
    )]


async def update_implementation(args: dict) -> list[TextContent]:
    """Update implementation documentation."""
    feature_name = args.get("feature_name")
    if not feature_name or feature_name not in FEATURES:
        raise ValueError(f"Feature '{feature_name}' not found")

    content = args.get("content", "")
    FEATURES[feature_name]["implementation"] += f"\n\n{content}"

    return [TextContent(
        type="text",
        text=json.dumps({"status": "updated", "feature": feature_name}, indent=2)
    )]


async def add_debug_log(args: dict) -> list[TextContent]:
    """Add a debug log entry."""
    feature_name = args.get("feature_name")
    if not feature_name or feature_name not in FEATURES:
        raise ValueError(f"Feature '{feature_name}' not found")

    log_entry = {
        "attempt": args.get("attempt", 1),
        "error": args.get("error", ""),
        "log": args.get("log", ""),
    }

    FEATURES[feature_name]["debug_logs"].append(log_entry)

    return [TextContent(
        type="text",
        text=json.dumps({"status": "logged", "attempt": log_entry["attempt"]}, indent=2)
    )]


async def get_feature(args: dict) -> list[TextContent]:
    """Get feature details."""
    name = args.get("name")
    if not name or name not in FEATURES:
        raise ValueError(f"Feature '{name}' not found")

    return [TextContent(
        type="text",
        text=json.dumps(FEATURES[name], indent=2)
    )]


async def generate_wiki(args: dict) -> list[TextContent]:
    """Generate wiki page for a feature."""
    feature_name = args.get("feature_name")
    if not feature_name or feature_name not in FEATURES:
        raise ValueError(f"Feature '{feature_name}' not found")

    feature = FEATURES[feature_name]
    fmt = args.get("format", "markdown")

    if fmt == "html":
        wiki = generate_html_wiki(feature)
    else:
        wiki = generate_markdown_wiki(feature)

    return [TextContent(type="text", text=wiki)]


def generate_markdown_wiki(feature: dict) -> str:
    """Generate Markdown wiki page."""
    lines = [
        f"# {feature['name']}",
        "",
        f"**Version:** {feature['version']}",
        f"**Status:** {feature['status']}",
        "",
        f"## Description",
        "",
        feature.get("description", "No description provided."),
        "",
    ]

    if feature.get("tags"):
        lines.extend([
            "## Tags",
            "",
            ", ".join(f"`{tag}`" for tag in feature["tags"]),
            "",
        ])

    if feature.get("plan"):
        lines.extend([
            "## Plan",
            "",
            feature["plan"],
            "",
        ])

    if feature.get("implementation"):
        lines.extend([
            "## Implementation",
            "",
            feature["implementation"],
            "",
        ])

    if feature.get("steps"):
        lines.append("## Implementation Steps")
        lines.append("")
        for i, step in enumerate(feature["steps"], 1):
            lines.append(f"### Step {i}: {step['step']}")
            lines.append("")
            if step.get("command"):
                lines.append("```bash")
                lines.append(step["command"])
                lines.append("```")
                lines.append("")
            if step.get("files_modified"):
                lines.append("**Files modified:**")
                for f in step["files_modified"]:
                    lines.append(f"- `{f}`")
                lines.append("")
            if step.get("output"):
                lines.append("**Output:**")
                lines.append("```")
                lines.append(step["output"][:500])
                lines.append("```")
                lines.append("")
            lines.append(f"**Status:** {step.get('status', 'unknown')}")
            lines.append("")

    if feature.get("debug_logs"):
        lines.extend([
            "## Debug Logs",
            "",
        ])
        for log in feature["debug_logs"]:
            lines.append(f"### Attempt {log['attempt']}")
            lines.append("")
            lines.append(f"**Error:** {log.get('error', 'N/A')}")
            lines.append("")
            if log.get("log"):
                lines.append("```")
                lines.append(log["log"])
                lines.append("```")
                lines.append("")

    return "\n".join(lines)


def generate_html_wiki(feature: dict) -> str:
    """Generate HTML wiki page."""
    md = generate_markdown_wiki(feature)
    # Simple markdown to HTML conversion
    html = md.replace("# ", "<h1>").replace("\n## ", "</h1>\n<h2>").replace("\n### ", "</h2>\n<h3>")
    html = html.replace("**", "<strong>").replace("`", "<code>")
    html = html.replace("\n\n", "</p>\n<p>")
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>{feature['name']} - SchemaWiki</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1, h2, h3 {{ color: #333; }}
        code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
        pre {{ background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }}
    </style>
</head>
<body>
{html}
</body>
</html>"""


async def list_features() -> list[TextContent]:
    """List all features."""
    return [TextContent(
        type="text",
        text=json.dumps(list(FEATURES.keys()), indent=2)
    )]


async def search_features(args: dict) -> list[TextContent]:
    """Search features."""
    query = args.get("query", "").lower()
    results = []

    for name, feature in FEATURES.items():
        if query in name.lower() or query in feature.get("description", "").lower():
            results.append(feature)

    return [TextContent(
        type="text",
        text=json.dumps(results, indent=2)
    )]


# REST API endpoints for external integration
@app.post("/features")
async def create_feature_api(feature: FeatureRecord):
    """REST API: Create feature."""
    args = feature.model_dump()
    result = await create_feature(args)
    return json.loads(result[0].text)


@app.post("/steps")
async def record_step_api(step: StepRecord):
    """REST API: Record step."""
    args = step.model_dump()
    result = await record_step(args)
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


@app.get("/health")
async def health():
    return {"status": "healthy"}


async def main():
    """Run the MCP server."""
    # Run both MCP stdio server and REST API
    import threading

    # Start REST API in background thread
    def run_api():
        uvicorn.run(app, host="0.0.0.0", port=8081, log_level="warning")

    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()

    # Run MCP server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(
                notification_options=NotificationOptions(),
                capabilities=server.get_capabilities(),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
