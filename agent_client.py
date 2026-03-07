"""SchemaWiki Agent Client - Python library for recording agent activities."""

import os
import json
from typing import Optional


class SchemaWikiClient:
    """Client for recording agent activities to SchemaWiki."""

    def __init__(
        self,
        api_url: str = "http://localhost:8081",
        feature_name: Optional[str] = None,
    ):
        """Initialize the client."""
        self.api_url = api_url.rstrip("/")
        self.feature_name = feature_name
        self._step_count = 0

    def set_feature(self, feature_name: str) -> None:
        """Set the current feature being worked on."""
        self.feature_name = feature_name

    def create_feature(
        self,
        name: str,
        description: str = "",
        version: str = "0.1.0",
        tags: list[str] = None,
        plan: str = "",
    ) -> dict:
        """Create a new feature record."""
        import requests

        response = requests.post(
            f"{self.api_url}/features",
            json={
                "name": name,
                "description": description,
                "version": version,
                "tags": tags or [],
                "plan_content": plan,
            },
            timeout=30,
        )
        response.raise_for_status()
        self.feature_name = name
        return response.json()

    def record_step(
        self,
        step: str,
        command: str = "",
        files_modified: list[str] = None,
        output: str = "",
        status: str = "completed",
    ) -> dict:
        """Record an implementation step."""
        if not self.feature_name:
            raise ValueError("No feature set. Call set_feature() or create_feature() first.")

        import requests

        response = requests.post(
            f"{self.api_url}/steps",
            json={
                "feature_name": self.feature_name,
                "step": step,
                "command": command,
                "files_modified": files_modified or [],
                "output": output[:2000] if output else "",  # Truncate long output
                "status": status,
            },
            timeout=30,
        )
        response.raise_for_status()
        self._step_count += 1
        return response.json()

    def record_command(
        self,
        description: str,
        command: str,
        output: str = "",
        status: str = "completed",
    ) -> dict:
        """Shorthand for recording a command execution."""
        return self.record_step(
            step=description,
            command=command,
            output=output,
            status=status,
        )

    def record_file_edit(
        self,
        file_path: str,
        description: str = "Edited file",
    ) -> dict:
        """Record a file modification."""
        return self.record_step(
            step=description,
            files_modified=[file_path],
            status="completed",
        )

    def record_test(
        self,
        test_name: str,
        passed: bool,
        output: str = "",
    ) -> dict:
        """Record test execution."""
        return self.record_step(
            step=f"Run test: {test_name}",
            output=output,
            status="completed" if passed else "failed",
        )

    def record_error(
        self,
        error: str,
        attempt: int = 1,
        log: str = "",
    ) -> dict:
        """Record an error or failed attempt."""
        import requests

        response = requests.post(
            f"{self.api_url}/features/{self.feature_name}/debug-log",
            json={
                "attempt": attempt,
                "error": error,
                "log": log,
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def update_implementation(self, content: str) -> dict:
        """Update the implementation documentation."""
        import requests

        response = requests.put(
            f"{self.api_url}/features/{self.feature_name}/implementation",
            json={"content": content},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def get_feature(self, name: Optional[str] = None) -> dict:
        """Get feature details."""
        feature_name = name or self.feature_name
        import requests

        response = requests.get(
            f"{self.api_url}/features/{feature_name}",
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def get_wiki(self, name: Optional[str] = None, format: str = "markdown") -> str:
        """Generate wiki page for the feature."""
        feature_name = name or self.feature_name
        import requests

        response = requests.get(
            f"{self.api_url}/wiki/{feature_name}",
            params={"format": format},
            timeout=30,
        )
        response.raise_for_status()
        return response.text

    def save_wiki(self, filename: str, name: Optional[str] = None, format: str = "markdown") -> None:
        """Save wiki page to file."""
        wiki = self.get_wiki(name, format)
        with open(filename, "w") as f:
            f.write(wiki)


# Decorator for automatic recording
def record_agent_activity(feature_name: str = None):
    """Decorator to automatically record function calls."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            client = SchemaWikiClient()
            if feature_name:
                client.set_feature(feature_name)

            # Record function call
            client.record_step(
                step=f"Execute: {func.__name__}",
                command=f"{func.__name__}({args}, {kwargs})",
                status="completed",
            )

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                client.record_error(error=str(e))
                raise

        return wrapper
    return decorator


# Example usage for an AI agent:
"""
from agent_client import SchemaWikiClient

# Initialize client
client = SchemaWikiClient(api_url="http://localhost:8081")

# Create a new feature
client.create_feature(
    name="user-auth-system",
    description="JWT-based authentication system",
    tags=["auth", "security"],
    plan="Implement login, logout, register endpoints"
)

# Record implementation steps
client.record_step(
    step="Create User model",
    command="sqlacodegen users.db > models.py",
    files_modified=["models.py"],
    status="completed"
)

client.record_step(
    step="Create login endpoint",
    command="touch routes/auth.py",
    files_modified=["routes/auth.py"],
    status="completed"
)

# Record a test
client.record_test(
    test_name="test_login_success",
    passed=True,
    output="1 passed, 0 failed"
)

# Generate wiki
wiki = client.get_wiki()
print(wiki)

# Save to file
client.save_wiki("user-auth-system.md")
"""
