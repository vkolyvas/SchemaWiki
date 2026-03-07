#!/usr/bin/env python3
"""SchemaWiki CLI - Command-line interface for SchemaWiki."""

import argparse
import json
import os
import sys
from typing import Optional

import requests


class SchemaWikiCLI:
    """CLI for SchemaWiki."""

    def __init__(self, api_url: str = "http://localhost:8081", github: bool = False):
        self.api_url = api_url.rstrip("/")
        self.github = github

    def create_feature(
        self,
        name: str,
        description: str = "",
        version: str = "1.0.0",
        tags: list[str] = None,
        plan: str = "",
        why: str = "",
    ) -> dict:
        """Create a new feature."""
        response = requests.post(
            f"{self.api_url}/features",
            json={
                "name": name,
                "description": description,
                "version": version,
                "tags": tags or [],
                "plan_content": plan,
                "why": why,
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def record_step(
        self,
        feature: str,
        step: str,
        why: str = "",
        trigger: str = "",
        command: str = "",
        files: list[str] = None,
        status: str = "completed",
    ) -> dict:
        """Record a step."""
        response = requests.post(
            f"{self.api_url}/steps",
            json={
                "feature_name": feature,
                "step": step,
                "why": why,
                "trigger": trigger,
                "command": command,
                "files_modified": files or [],
                "status": status,
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def record_event(
        self,
        feature: str,
        event_type: str,
        why: str,
        details: str = "",
        files: list[str] = None,
    ) -> dict:
        """Record an event."""
        response = requests.post(
            f"{self.api_url}/events",
            json={
                "feature_name": feature,
                "event_type": event_type,
                "why": why,
                "details": details,
                "files": files or [],
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def generate_wiki(
        self,
        feature: str,
        format: str = "markdown",
        push_to_github: bool = None,
    ) -> dict:
        """Generate wiki for a feature."""
        params = {"format": format}
        if push_to_github is not None:
            params["push_to_github"] = push_to_github
        elif self.github:
            params["push_to_github"] = True

        response = requests.get(
            f"{self.api_url}/wiki/{feature}",
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        return {"content": response.text, "status": "success"}

    def list_wikis(self) -> dict:
        """List all wikis."""
        response = requests.get(f"{self.api_url}/wikis", timeout=30)
        response.raise_for_status()
        return response.json()

    def get_feature(self, feature: str) -> dict:
        """Get feature details."""
        response = requests.get(f"{self.api_url}/features/{feature}", timeout=30)
        response.raise_for_status()
        return response.json()

    def list_features(self) -> list:
        """List all features."""
        response = requests.get(f"{self.api_url}/features", timeout=30)
        response.raise_for_status()
        return response.json()


def main():
    parser = argparse.ArgumentParser(description="SchemaWiki CLI")
    parser.add_argument(
        "--api-url",
        default=os.environ.get("SCHEMAWIKI_URL", "http://localhost:8081"),
        help="API URL (default: http://localhost:8081)",
    )
    parser.add_argument(
        "--github",
        action="store_true",
        help="Auto-push wikis to GitHub",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # create-feature
    create_parser = subparsers.add_parser("create", help="Create a new feature")
    create_parser.add_argument("name", help="Feature name")
    create_parser.add_argument("-d", "--description", default="", help="Description")
    create_parser.add_argument("-v", "--version", default="1.0.0", help="Version")
    create_parser.add_argument("-t", "--tags", help="Comma-separated tags")
    create_parser.add_argument("-p", "--plan", default="", help="Plan")
    create_parser.add_argument("-w", "--why", default="", help="Why this feature exists")

    # record-step
    step_parser = subparsers.add_parser("step", help="Record a step")
    step_parser.add_argument("-f", "--feature", required=True, help="Feature name")
    step_parser.add_argument("step", help="Step description")
    step_parser.add_argument("-w", "--why", default="", help="Why this step")
    step_parser.add_argument(
        "-t", "--trigger", default="", help="Trigger (user_request, error, etc)"
    )
    step_parser.add_argument("-c", "--command", default="", help="Command executed")
    step_parser.add_argument("--files", help="Comma-separated files modified")
    step_parser.add_argument("-s", "--status", default="completed", help="Status")

    # record-event
    event_parser = subparsers.add_parser("event", help="Record an event")
    event_parser.add_argument("-f", "--feature", required=True, help="Feature name")
    event_parser.add_argument("event_type", help="Event type")
    event_parser.add_argument("-w", "--why", required=True, help="Why this happened")
    event_parser.add_argument("-d", "--details", default="", help="Details")
    event_parser.add_argument("--files", help="Comma-separated files")

    # wiki
    wiki_parser = subparsers.add_parser("wiki", help="Generate wiki")
    wiki_parser.add_argument("feature", help="Feature name")
    wiki_parser.add_argument("-f", "--format", default="markdown", choices=["markdown", "html"])
    wiki_parser.add_argument("--push", action="store_true", dest="push", help="Push to GitHub")
    wiki_parser.add_argument("-o", "--output", help="Output file")

    # list-wikis
    subparsers.add_parser("wikis", help="List all wikis")

    # get-feature
    get_parser = subparsers.add_parser("get", help="Get feature details")
    get_parser.add_argument("feature", help="Feature name")

    # list-features
    subparsers.add_parser("list", help="List all features")

    args = parser.parse_args()

    cli = SchemaWikiCLI(api_url=args.api_url, github=args.github)

    try:
        if args.command == "create":
            tags = args.tags.split(",") if args.tags else None
            result = cli.create_feature(
                name=args.name,
                description=args.description,
                version=args.version,
                tags=tags,
                plan=args.plan,
                why=args.why,
            )
            print(json.dumps(result, indent=2))

        elif args.command == "step":
            files = args.files.split(",") if args.files else None
            result = cli.record_step(
                feature=args.feature,
                step=args.step,
                why=args.why,
                trigger=args.trigger,
                command=args.command,
                files=files,
                status=args.status,
            )
            print(json.dumps(result, indent=2))

        elif args.command == "event":
            files = args.files.split(",") if args.files else None
            result = cli.record_event(
                feature=args.feature,
                event_type=args.event_type,
                why=args.why,
                details=args.details,
                files=files,
            )
            print(json.dumps(result, indent=2))

        elif args.command == "wiki":
            result = cli.generate_wiki(
                feature=args.feature,
                format=args.format,
                push_to_github=args.push,
            )
            if args.output:
                with open(args.output, "w") as f:
                    f.write(result["content"])
                print(f"Wiki saved to {args.output}")
            else:
                print(result["content"])

        elif args.command == "wikis":
            result = cli.list_wikis()
            print(json.dumps(result, indent=2))

        elif args.command == "get":
            result = cli.get_feature(args.feature)
            print(json.dumps(result, indent=2))

        elif args.command == "list":
            result = cli.list_features()
            print(json.dumps(result, indent=2))

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
