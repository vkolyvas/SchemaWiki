"""Git operations for feature versioning and commit tracking."""

import os
from pathlib import Path
from typing import Optional
import subprocess
from datetime import datetime


class GitRepo:
    """Handle Git operations for features."""

    def __init__(self, features_path: str):
        """Initialize Git repo at features path."""
        self.features_path = Path(features_path)

    def _run_git(self, *args, cwd: Optional[Path] = None) -> str:
        """Run a git command."""
        if cwd is None:
            cwd = self.features_path

        result = subprocess.run(
            ["git"] + list(args),
            cwd=cwd,
            capture_output=True,
            text=True,
            env=self._get_git_env()
        )

        if result.returncode != 0:
            raise RuntimeError(f"Git command failed: {result.stderr}")

        return result.stdout.strip()

    def _get_git_env(self) -> dict:
        """Get environment for git operations."""
        env = os.environ.copy()
        env["GIT_AUTHOR_NAME"] = os.getenv("GIT_AUTHOR_NAME", "SchemaWiki")
        env["GIT_AUTHOR_EMAIL"] = os.getenv("GIT_AUTHOR_EMAIL", "schemawiki@localhost")
        env["GIT_COMMITTER_NAME"] = env["GIT_AUTHOR_NAME"]
        env["GIT_COMMITTER_EMAIL"] = env["GIT_AUTHOR_EMAIL"]
        return env

    def init(self) -> None:
        """Initialize git repo if not already initialized."""
        if not (self.features_path / ".git").exists():
            self._run_git("init")
            self._run_git("config", "user.name", os.getenv("GIT_AUTHOR_NAME", "SchemaWiki"))
            self._run_git("config", "user.email", os.getenv("GIT_AUTHOR_EMAIL", "schemawiki@localhost"))

    def is_repo(self) -> bool:
        """Check if features path is a git repo."""
        return (self.features_path / ".git").exists()

    def commit_feature_change(
        self,
        feature_name: str,
        message: str,
        files: Optional[list[str]] = None
    ) -> str:
        """Commit changes to a feature."""
        if not self.is_repo():
            self.init()

        feature_path = self.features_path / feature_name

        if not feature_path.exists():
            raise ValueError(f"Feature {feature_name} does not exist")

        # Add files
        if files:
            for file in files:
                self._run_git("add", str(feature_path / file))
        else:
            self._run_git("add", str(feature_path))

        # Check if there are changes to commit
        status = self._run_git("status", "--porcelain")
        if not status:
            return self.get_latest_commit_hash()

        # Commit with message
        commit_message = f"{message}\n\nFeature: {feature_name}"
        self._run_git("commit", "-m", commit_message)

        return self.get_latest_commit_hash()

    def get_latest_commit_hash(self, feature_name: Optional[str] = None) -> str:
        """Get the latest commit hash."""
        if feature_name:
            path = self.features_path / feature_name
            try:
                return self._run_git("log", "-1", "--format=%H", "--", str(path))
            except RuntimeError:
                return ""
        return self._run_git("log", "-1", "--format=%H")

    def get_commit_history(self, feature_name: str, max_count: int = 10) -> list[dict]:
        """Get commit history for a feature."""
        if not self.is_repo():
            return []

        feature_path = self.features_path / feature_name
        if not feature_path.exists():
            return []

        try:
            format_str = "%H|%an|%ae|%at|%s"
            output = self._run_git(
                "log",
                f"--max-count={max_count}",
                f"--format={format_str}",
                "--",
                str(feature_path)
            )

            commits = []
            for line in output.split("\n"):
                if "|" in line:
                    parts = line.split("|")
                    commits.append({
                        "hash": parts[0],
                        "author": parts[1],
                        "email": parts[2],
                        "timestamp": int(parts[3]),
                        "message": parts[4] if len(parts) > 4 else ""
                    })
            return commits
        except RuntimeError:
            return []

    def get_current_branch(self) -> str:
        """Get current branch name."""
        if not self.is_repo():
            return "main"
        return self._run_git("branch", "--show-current")

    def create_branch(self, branch_name: str) -> None:
        """Create a new branch."""
        self._run_git("checkout", "-b", branch_name)

    def checkout_branch(self, branch_name: str) -> None:
        """Checkout a branch."""
        self._run_git("checkout", branch_name)

    def get_file_diff(self, feature_name: str, commit_hash: str) -> str:
        """Get diff for a feature at a specific commit."""
        feature_path = self.features_path / feature_name
        try:
            return self._run_git("show", f"{commit_hash}:{feature_name}")
        except RuntimeError:
            return ""
