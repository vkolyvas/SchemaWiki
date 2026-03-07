"""Filesystem operations for feature directories."""

import json
import os
import shutil
from pathlib import Path
from typing import Optional

import yaml


class FileStore:
    """Handle filesystem operations for features."""

    # Standard feature files
    PLAN_FILE = "plan.md"
    IMPLEMENTATION_FILE = "implementation.md"
    AGENT_STEPS_FILE = "agent_steps.yaml"
    REPLAY_PROTOCOL_FILE = "replay_protocol.json"
    ARCHITECTURE_FILE = "architecture.md"
    API_CONTRACTS_FILE = "api_contracts.yaml"
    TESTS_FILE = "tests.md"
    DEBUG_LOGS_DIR = "debug_logs"

    def __init__(self, base_path: Optional[str] = None):
        """Initialize file store with base path."""
        if base_path is None:
            from storage.metadata_db import get_features_data_path

            base_path = get_features_data_path()
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def get_feature_path(self, feature_name: str) -> Path:
        """Get path to feature directory."""
        # Sanitize feature name
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in feature_name)
        return self.base_path / safe_name

    def feature_exists(self, feature_name: str) -> bool:
        """Check if feature directory exists."""
        return self.get_feature_path(feature_name).exists()

    def create_feature_dir(self, feature_name: str) -> Path:
        """Create feature directory with standard structure."""
        feature_path = self.get_feature_path(feature_name)
        feature_path.mkdir(parents=True, exist_ok=True)

        # Create debug logs subdirectory
        (feature_path / self.DEBUG_LOGS_DIR).mkdir(exist_ok=True)

        # Create empty standard files
        for filename in [
            self.PLAN_FILE,
            self.IMPLEMENTATION_FILE,
            self.AGENT_STEPS_FILE,
            self.ARCHITECTURE_FILE,
            self.API_CONTRACTS_FILE,
            self.TESTS_FILE,
        ]:
            file_path = feature_path / filename
            if not file_path.exists():
                file_path.write_text("")

        return feature_path

    def read_file(self, feature_name: str, filename: str) -> Optional[str]:
        """Read a file from feature directory."""
        file_path = self.get_feature_path(feature_name) / filename
        if file_path.exists():
            return file_path.read_text()
        return None

    def write_file(self, feature_name: str, filename: str, content: str) -> Path:
        """Write content to a file in feature directory."""
        feature_path = self.get_feature_path(feature_name)
        file_path = feature_path / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        return file_path

    def delete_feature(self, feature_name: str) -> None:
        """Delete feature directory."""
        feature_path = self.get_feature_path(feature_name)
        if feature_path.exists():
            shutil.rmtree(feature_path)

    def list_features(self) -> list[str]:
        """List all features in the base path."""
        if not self.base_path.exists():
            return []
        return [d.name for d in self.base_path.iterdir() if d.is_dir()]

    def get_all_files(self, feature_name: str) -> dict[str, str]:
        """Get all standard files for a feature."""
        feature_path = self.get_feature_path(feature_name)
        if not feature_path.exists():
            return {}

        files = {}
        for filename in [
            self.PLAN_FILE,
            self.IMPLEMENTATION_FILE,
            self.AGENT_STEPS_FILE,
            self.REPLAY_PROTOCOL_FILE,
            self.ARCHITECTURE_FILE,
            self.API_CONTRACTS_FILE,
            self.TESTS_FILE,
        ]:
            file_path = feature_path / filename
            if file_path.exists():
                files[filename] = file_path.read_text()

        return files

    def write_replay_protocol(self, feature_name: str, protocol: dict) -> Path:
        """Write replay protocol JSON."""
        return self.write_file(
            feature_name, self.REPLAY_PROTOCOL_FILE, json.dumps(protocol, indent=2)
        )

    def read_replay_protocol(self, feature_name: str) -> Optional[dict]:
        """Read replay protocol JSON."""
        content = self.read_file(feature_name, self.REPLAY_PROTOCOL_FILE)
        if content:
            return json.loads(content)
        return None

    def write_agent_steps(self, feature_name: str, steps: list) -> Path:
        """Write agent steps YAML."""
        return self.write_file(
            feature_name, self.AGENT_STEPS_FILE, yaml.dump(steps, default_flow_style=False)
        )

    def read_agent_steps(self, feature_name: str) -> Optional[list]:
        """Read agent steps YAML."""
        content = self.read_file(feature_name, self.AGENT_STEPS_FILE)
        if content:
            return yaml.safe_load(content)
        return None

    def add_debug_log(self, feature_name: str, attempt_number: int, log_content: str) -> Path:
        """Add a debug log for a failed attempt."""
        feature_path = self.get_feature_path(feature_name)
        debug_dir = feature_path / self.DEBUG_LOGS_DIR
        debug_dir.mkdir(parents=True, exist_ok=True)

        log_file = debug_dir / f"attempt_{attempt_number}.log"
        log_file.write_text(log_content)
        return log_file

    def get_debug_logs(self, feature_name: str) -> list[dict]:
        """Get all debug logs for a feature."""
        feature_path = self.get_feature_path(feature_name)
        debug_dir = feature_path / self.DEBUG_LOGS_DIR

        if not debug_dir.exists():
            return []

        logs = []
        for log_file in sorted(debug_dir.glob("attempt_*.log")):
            logs.append(
                {"attempt": int(log_file.stem.split("_")[1]), "content": log_file.read_text()}
            )
        return logs
