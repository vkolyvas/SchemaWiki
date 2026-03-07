"""SchemaWiki Agent Client - Python library for recording agent activities with rich context."""

import json
import os
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
        why: str = "",  # Why this feature exists
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
                "why": why,  # Why this feature is being built
            },
            timeout=30,
        )
        response.raise_for_status()
        self.feature_name = name
        return response.json()

    def record_step(
        self,
        step: str,
        why: str = "",  # Why this step was taken
        trigger: str = "",  # What triggered this
        command: str = "",
        files_modified: list[str] = None,
        output: str = "",
        status: str = "completed",
        context: str = "",
    ) -> dict:
        """Record an implementation step with reasoning."""
        if not self.feature_name:
            raise ValueError("No feature set. Call set_feature() or create_feature() first.")

        import requests

        response = requests.post(
            f"{self.api_url}/steps",
            json={
                "feature_name": self.feature_name,
                "step": step,
                "why": why,
                "trigger": trigger,
                "command": command,
                "files_modified": files_modified or [],
                "output": output[:2000] if output else "",
                "status": status,
                "context": context,
            },
            timeout=30,
        )
        response.raise_for_status()
        self._step_count += 1
        return response.json()

    def record_event(
        self,
        event_type: str,
        why: str = "",  # Why this happened
        details: str = "",
        files: list[str] = None,
    ) -> dict:
        """Record a development event (restart, push, test, etc.) with reasoning."""
        if not self.feature_name:
            raise ValueError("No feature set. Call set_feature() or create_feature() first.")

        import requests

        response = requests.post(
            f"{self.api_url}/events",
            json={
                "feature_name": self.feature_name,
                "event_type": event_type,
                "why": why,
                "details": details,
                "files": files or [],
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    # Convenience methods for common events

    def feature_coded(self, why: str, details: str = "", files: list[str] = None) -> dict:
        """Record that a feature was coded."""
        return self.record_event("feature_coded", why, details, files)

    def service_restarted(self, why: str, details: str = "") -> dict:
        """Record a service restart."""
        return self.record_event("service_restarted", why, details)

    def change_pushed(self, why: str, files: list[str] = None) -> dict:
        """Record a git push."""
        return self.record_event("change_pushed", why, files=files)

    def missing_code(self, why: str, details: str = "", files: list[str] = None) -> dict:
        """Record that something was missing from the code."""
        return self.record_event("missing_code", why, details, files)

    def lint_error(self, why: str, details: str = "", files: list[str] = None) -> dict:
        """Record a lint error."""
        return self.record_event("lint_error", why, details, files)

    def test_passed(self, why: str, details: str = "") -> dict:
        """Record a passing test."""
        return self.record_event("test_passed", why, details)

    def test_failed(self, why: str, details: str = "", files: list[str] = None) -> dict:
        """Record a failing test."""
        return self.record_event("test_failed", why, details, files)

    def bug_fix(self, why: str, details: str = "", files: list[str] = None) -> dict:
        """Record a bug fix."""
        return self.record_event("bug_fix", why, details, files)

    def code_review(self, why: str, details: str = "", files: list[str] = None) -> dict:
        """Record a code review finding."""
        return self.record_event("code_review", why, details, files)

    def refactor(self, why: str, details: str = "", files: list[str] = None) -> dict:
        """Record a refactoring."""
        return self.record_event("refactor", why, details, files)

    def dependency_added(self, why: str, details: str = "", files: list[str] = None) -> dict:
        """Record adding a dependency."""
        return self.record_event("dependency_added", why, details, files)

    def config_changed(self, why: str, details: str = "", files: list[str] = None) -> dict:
        """Record a config change."""
        return self.record_event("config_changed", why, details, files)

    def api_contract_change(self, why: str, details: str = "", files: list[str] = None) -> dict:
        """Record an API contract change."""
        return self.record_event("api_contract_change", why, details, files)

    def db_migration(self, why: str, details: str = "", files: list[str] = None) -> dict:
        """Record a database migration."""
        return self.record_event("db_migration", why, details, files)

    # Record methods with reasoning

    def record_command(
        self,
        description: str,
        command: str,
        why: str = "",
        trigger: str = "",
        output: str = "",
        status: str = "completed",
    ) -> dict:
        """Shorthand for recording a command with reasoning."""
        return self.record_step(
            step=description,
            why=why,
            trigger=trigger,
            command=command,
            output=output,
            status=status,
        )

    def record_file_edit(
        self,
        file_path: str,
        why: str = "",
        trigger: str = "",
        description: str = "Edited file",
    ) -> dict:
        """Record a file modification with reasoning."""
        return self.record_step(
            step=description,
            why=why,
            trigger=trigger,
            files_modified=[file_path],
            status="completed",
        )

    def record_test(
        self,
        test_name: str,
        passed: bool,
        why: str = "",
        output: str = "",
    ) -> dict:
        """Record test execution with reasoning."""
        event_type = "test_passed" if passed else "test_failed"
        return self.record_event(
            event_type=event_type,
            why=why,
            details=f"Test: {test_name}",
        )

    def record_error(
        self,
        error: str,
        why_failed: str = "",  # Root cause
        fix_applied: str = "",  # What was done to fix
        attempt: int = 1,
        log: str = "",
    ) -> dict:
        """Record an error with root cause analysis."""
        import requests

        response = requests.post(
            f"{self.api_url}/features/{self.feature_name}/debug-log",
            json={
                "attempt": attempt,
                "error": error,
                "why_failed": why_failed,
                "fix_applied": fix_applied,
                "log": log,
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def update_implementation(self, content: str, why: str = "") -> dict:
        """Update the implementation documentation with reasoning."""
        import requests

        response = requests.put(
            f"{self.api_url}/features/{self.feature_name}/implementation",
            json={"content": content, "why": why},
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

    def save_wiki(
        self, filename: str, name: Optional[str] = None, format: str = "markdown"
    ) -> None:
        """Save wiki page to file."""
        wiki = self.get_wiki(name, format)
        with open(filename, "w") as f:
            f.write(wiki)


# Example usage:
"""
from agent_client import SchemaWikiClient

client = SchemaWikiClient(api_url="http://localhost:8081")

# Create feature with WHY
client.create_feature(
    name="user-auth-system",
    description="JWT-based authentication",
    tags=["auth", "security"],
    plan="Implement login, logout, register",
    why="Users need secure authentication to access protected resources"
)

# Record a step with WHY and TRIGGER
client.record_step(
    step="Create User model",
    why="Need to store user credentials and profile data",
    trigger="feature_requirement",
    command="sqlacodegen users.db > models.py",
    files_modified=["models.py"],
    status="completed"
)

# Record events with WHY
client.service_restarted(
    why="Applied new environment variables for JWT secret",
    details="Restarted to load new config"
)

client.lint_error(
    why="Code didn't follow PEP 8",
    details="Line too long warnings",
    files=["auth.py"]
)

client.test_failed(
    why="Test expected different response format",
    details="API returned JSON but test expected XML"
)

client.bug_fix(
    why="Token wasn't being validated properly",
    details="Added missing expiry check",
    files=["middleware/auth.py"]
)

client.change_pushed(
    why="Completed authentication feature",
    files=["models.py", "routes/auth.py", "middleware/auth.py"]
)

# Record error with root cause
client.record_error(
    error="Connection refused to database",
    why_failed="Database wasn't running in Docker network",
    fix_applied="Added database to docker-compose services",
    attempt=1
)

# Generate wiki
wiki = client.get_wiki()
print(wiki)
"""
