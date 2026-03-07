"""Agent CLI for SchemaWiki."""

import os
import sys
import asyncio
import json
from typing import Optional

import typer
import httpx
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="SchemaWiki - AI-native feature documentation system")
console = Console()


API_BASE_URL = os.getenv("SCHEMAWIKI_API_URL", "http://localhost:8080")


def get_api_client() -> httpx.AsyncClient:
    """Get HTTP client for API."""
    return httpx.AsyncClient(base_url=API_BASE_URL, timeout=30.0)


@app.command()
def record_feature(
    name: str = typer.Argument(..., help="Feature name"),
    description: str = typer.Option(None, "--description", "-d", help="Feature description"),
    version: str = typer.Option("0.1.0", "--version", "-v", help="Initial version"),
    tags: str = typer.Option(None, "--tags", "-t", help="Comma-separated tags"),
    plan: str = typer.Option(None, "--plan", "-p", help="Plan content or file path"),
):
    """Record a new feature."""
    tag_list = [t.strip() for t in tags.split(",")] if tags else None

    # Check if plan is a file path
    plan_content = None
    if plan and os.path.isfile(plan):
        plan_content = open(plan).read()
    elif plan:
        plan_content = plan

    async def _create():
        client = get_api_client()
        try:
            response = await client.post(
                "/features",
                json={
                    "name": name,
                    "description": description,
                    "version": version,
                    "tags": tag_list,
                    "plan_content": plan_content,
                },
            )
            response.raise_for_status()
            data = response.json()
            console.print(f"[green]Feature '{name}' created successfully![/green]")
            console.print(f"Version: {data['version']}")
            console.print(f"Files: {len(data['files'])}")
            return data
        except httpx.HTTPStatusError as e:
            console.print(f"[red]Error:[/red] {e.response.json().get('detail', str(e))}")
            raise typer.Exit(1)
        finally:
            await client.aclose()

    asyncio.run(_create())


@app.command()
def get_plan(
    name: str = typer.Argument(..., help="Feature name"),
    output: str = typer.Option(None, "--output", "-o", help="Output file for plan"),
):
    """Get feature plan."""
    async def _get():
        client = get_api_client()
        try:
            response = await client.get(f"/features/{name}")
            response.raise_for_status()
            data = response.json()

            plan_content = data["files"]["plan"]

            if output:
                with open(output, "w") as f:
                    f.write(plan_content)
                console.print(f"[green]Plan saved to {output}[/green]")
            else:
                console.print(plan_content)

            return data
        except httpx.HTTPStatusError as e:
            console.print(f"[red]Error:[/red] {e.response.json().get('detail', str(e))}")
            raise typer.Exit(1)
        finally:
            await client.aclose()

    asyncio.run(_get())


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    tags: str = typer.Option(None, "--tags", "-t", help="Filter by tags"),
    limit: int = typer.Option(10, "--limit", "-l", help="Max results"),
):
    """Search features."""
    async def _search():
        client = get_api_client()
        try:
            params = {"q": query, "limit": limit}
            if tags:
                params["tags"] = tags

            response = await client.get("/search", params=params)
            response.raise_for_status()
            data = response.json()

            if data["results"]:
                table = Table(title=f"Search Results for '{query}'")
                table.add_column("Name", style="cyan")
                table.add_column("Version", style="magenta")
                table.add_column("Status", style="green")
                table.add_column("Match Type", style="yellow")

                for result in data["results"]:
                    table.add_row(
                        result["name"],
                        result["version"],
                        result["status"],
                        result.get("match_type", "unknown"),
                    )

                console.print(table)
                console.print(f"\nTotal: {data['total']} results")
            else:
                console.print("[yellow]No results found[/yellow]")

            return data
        except httpx.HTTPStatusError as e:
            console.print(f"[red]Error:[/red] {e.response.json().get('detail', str(e))}")
            raise typer.Exit(1)
        finally:
            await client.aclose()

    asyncio.run(_search())


@app.command()
def recreate(
    name: str = typer.Argument(..., help="Feature name"),
    output_dir: str = typer.Option(None, "--output", "-o", help="Output directory"),
    include_debug: bool = typer.Option(False, "--debug", "-d", help="Include debug logs"),
):
    """Get replay protocol to recreate a feature."""
    async def _recreate():
        client = get_api_client()
        try:
            response = await client.get(
                f"/features/{name}/replay",
                params={"include_debug_logs": include_debug},
            )
            response.raise_for_status()
            protocol = response.json()

            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, "replay_protocol.json")
                with open(output_path, "w") as f:
                    json.dump(protocol, f, indent=2)
                console.print(f"[green]Replay protocol saved to {output_path}[/green]")
            else:
                console.print_json(data=protocol)

            console.print(f"\n[cyan]Total steps:[/cyan] {len(protocol.get('steps', []))}")

            return protocol
        except httpx.HTTPStatusError as e:
            console.print(f"[red]Error:[/red] {e.response.json().get('detail', str(e))}")
            raise typer.Exit(1)
        finally:
            await client.aclose()

    asyncio.run(_recreate())


@app.command()
def list_features(
    status: str = typer.Option(None, "--status", "-s", help="Filter by status"),
    tag: str = typer.Option(None, "--tag", "-t", help="Filter by tag"),
):
    """List all features."""
    async def _list():
        client = get_api_client()
        try:
            params = {}
            if status:
                params["status"] = status
            if tag:
                params["tag"] = tag

            response = await client.get("/features", params=params)
            response.raise_for_status()
            features = response.json()

            if features:
                table = Table(title="Features")
                table.add_column("Name", style="cyan")
                table.add_column("Version", style="magenta")
                table.add_column("Status", style="green")
                table.add_column("Tags", style="yellow")

                for feature in features:
                    table.add_row(
                        feature["name"],
                        feature["version"],
                        feature["status"],
                        ", ".join(feature.get("tags", [])),
                    )

                console.print(table)
                console.print(f"\nTotal: {len(features)} features")
            else:
                console.print("[yellow]No features found[/yellow]")

            return features
        except httpx.HTTPStatusError as e:
            console.print(f"[red]Error:[/red] {e.response.json().get('detail', str(e))}")
            raise typer.Exit(1)
        finally:
            await client.aclose()

    asyncio.run(_list())


@app.command()
def update_file(
    name: str = typer.Argument(..., help="Feature name"),
    filename: str = typer.Argument(..., help="File to update (e.g., plan.md, implementation.md)"),
    content: str = typer.Argument(..., help="Content or @filename to read from file"),
):
    """Update a feature file."""
    # Check if content is a file reference
    file_content = None
    if content.startswith("@"):
        file_path = content[1:]
        if os.path.isfile(file_path):
            with open(file_path) as f:
                file_content = f.read()
        else:
            console.print(f"[red]File not found:[/red] {file_path}")
            raise typer.Exit(1)
    else:
        file_content = content

    async def _update():
        client = get_api_client()
        try:
            response = await client.put(
                f"/features/{name}/files",
                json={
                    "filename": filename,
                    "content": file_content,
                    "commit_message": f"Update {filename}",
                },
            )
            response.raise_for_status()
            console.print(f"[green]File '{filename}' updated successfully![/green]")
            return response.json()
        except httpx.HTTPStatusError as e:
            console.print(f"[red]Error:[/red] {e.response.json().get('detail', str(e))}")
            raise typer.Exit(1)
        finally:
            await client.aclose()

    asyncio.run(_update())


if __name__ == "__main__":
    app()
