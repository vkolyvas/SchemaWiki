"""Replay engine for generating replay_protocol.json from feature files."""

import json
from pathlib import Path
from typing import Optional

import yaml

from storage.file_store import FileStore


class ReplayEngine:
    """Generate replay protocols from feature files."""

    def __init__(self, file_store: Optional[FileStore] = None):
        """Initialize replay engine."""
        self.file_store = file_store or FileStore()

    def generate_replay_protocol(
        self,
        feature_name: str,
        include_debug_logs: bool = True,
    ) -> dict:
        """Generate replay protocol from feature files."""
        if not self.file_store.feature_exists(feature_name):
            raise ValueError(f"Feature '{feature_name}' not found")

        # Read source files
        plan = self.file_store.read_file(feature_name, FileStore.PLAN_FILE) or ""
        implementation = (
            self.file_store.read_file(feature_name, FileStore.IMPLEMENTATION_FILE) or ""
        )
        agent_steps = self.file_store.read_agent_steps(feature_name) or []
        architecture = self.file_store.read_file(feature_name, FileStore.ARCHITECTURE_FILE) or ""
        api_contracts = self.file_store.read_file(feature_name, FileStore.API_CONTRACTS_FILE) or ""
        tests = self.file_store.read_file(feature_name, FileStore.TESTS_FILE) or ""

        # Extract steps
        steps = self._extract_steps(agent_steps, implementation)

        # Build protocol
        protocol = {
            "version": "1.0",
            "feature_name": feature_name,
            "plan": {
                "content": plan,
                "file_path": str(
                    self.file_store.get_feature_path(feature_name) / FileStore.PLAN_FILE
                ),
            },
            "implementation": {
                "content": implementation,
                "file_path": str(
                    self.file_store.get_feature_path(feature_name) / FileStore.IMPLEMENTATION_FILE
                ),
            },
            "steps": steps,
            "architecture": {
                "content": architecture,
                "file_path": str(
                    self.file_store.get_feature_path(feature_name) / FileStore.ARCHITECTURE_FILE
                ),
            },
            "api_contracts": {
                "content": api_contracts,
                "file_path": str(
                    self.file_store.get_feature_path(feature_name) / FileStore.API_CONTRACTS_FILE
                ),
            },
            "tests": {
                "content": tests,
                "file_path": str(
                    self.file_store.get_feature_path(feature_name) / FileStore.TESTS_FILE
                ),
            },
        }

        # Add debug logs if requested
        if include_debug_logs:
            debug_logs = self.file_store.get_debug_logs(feature_name)
            protocol["debug_logs"] = debug_logs

        return protocol

    def _extract_steps(self, agent_steps: list, implementation: str) -> list[dict]:
        """Extract steps from agent_steps.yaml and implementation.md."""
        steps = []

        # Add steps from agent_steps.yaml
        for step in agent_steps:
            step_dict = {
                "order": step.get("order", len(steps) + 1),
                "description": step.get("description", ""),
                "command": step.get("command", ""),
                "files_modified": step.get("files_modified", []),
                "expected_output": step.get("expected_output", ""),
            }
            steps.append(step_dict)

        # If no agent steps, try to extract from implementation
        if not steps and implementation:
            # Parse implementation for step-like patterns
            lines = implementation.split("\n")
            current_step = None

            for line in lines:
                # Look for numbered steps or headers
                if line.strip().startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.")):
                    if current_step:
                        steps.append(current_step)
                    current_step = {
                        "order": len(steps) + 1,
                        "description": line.strip()[2:].strip(),
                        "command": "",
                        "files_modified": [],
                        "expected_output": "",
                    }
                elif current_step and line.strip().startswith("```"):
                    # Code block - could be a command
                    if not current_step["command"]:
                        current_step["command"] = line.strip()

            if current_step:
                steps.append(current_step)

        return steps

    def save_replay_protocol(
        self,
        feature_name: str,
        include_debug_logs: bool = True,
    ) -> Path:
        """Generate and save replay protocol to file."""
        protocol = self.generate_replay_protocol(
            feature_name, include_debug_logs=include_debug_logs
        )
        return self.file_store.write_replay_protocol(feature_name, protocol)

    def get_step_summary(self, feature_name: str) -> dict:
        """Get a summary of steps for a feature."""
        protocol = self.generate_replay_protocol(feature_name, include_debug_logs=False)

        return {
            "feature_name": feature_name,
            "total_steps": len(protocol["steps"]),
            "steps": [
                {
                    "order": s["order"],
                    "description": s["description"][:100],
                    "has_command": bool(s["command"]),
                }
                for s in protocol["steps"]
            ],
        }
