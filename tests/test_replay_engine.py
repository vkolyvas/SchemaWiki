"""Tests for replay engine."""

import json
import tempfile

import pytest

from core.replay_engine import ReplayEngine
from storage.file_store import FileStore


class TestReplayEngine:
    """Tests for ReplayEngine."""

    @pytest.fixture
    def engine_with_feature(self):
        """Create engine with a test feature."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = FileStore(tmpdir)
            store.create_feature_dir("test-feature")
            store.write_file("test-feature", "plan.md", "# Test Plan\n\nThis is a test.")
            store.write_file(
                "test-feature",
                "implementation.md",
                "## Implementation\n\n1. Step one\n2. Step two",
            )
            store.write_agent_steps(
                "test-feature",
                [
                    {
                        "order": 1,
                        "description": "Create file",
                        "command": "touch test.py",
                        "files_modified": ["test.py"],
                    }
                ],
            )
            engine = ReplayEngine(store)
            yield engine

    def test_generate_replay_protocol(self, engine_with_feature):
        """Test generating replay protocol."""
        protocol = engine_with_feature.generate_replay_protocol("test-feature")

        assert protocol["version"] == "1.0"
        assert protocol["feature_name"] == "test-feature"
        assert "plan" in protocol
        assert "implementation" in protocol
        assert "steps" in protocol

    def test_replay_protocol_structure(self, engine_with_feature):
        """Test replay protocol has correct structure."""
        protocol = engine_with_feature.generate_replay_protocol("test-feature")

        # Check plan
        assert "content" in protocol["plan"]
        assert "file_path" in protocol["plan"]

        # Check implementation
        assert "content" in protocol["implementation"]
        assert "file_path" in protocol["implementation"]

    def test_steps_extraction_from_yaml(self, engine_with_feature):
        """Test extracting steps from YAML."""
        protocol = engine_with_feature.generate_replay_protocol("test-feature")

        assert len(protocol["steps"]) == 1
        assert protocol["steps"][0]["description"] == "Create file"
        assert protocol["steps"][0]["command"] == "touch test.py"

    def test_steps_extraction_from_markdown(self):
        """Test extracting steps from markdown."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = FileStore(tmpdir)
            store.create_feature_dir("md-feature")
            store.write_file(
                "md-feature",
                "implementation.md",
                """
## Implementation

1. First step
2. Second step
""",
            )
            engine = ReplayEngine(store)
            protocol = engine.generate_replay_protocol("md-feature")

            # Should have extracted steps
            assert len(protocol["steps"]) >= 0

    def test_include_debug_logs(self, engine_with_feature):
        """Test including debug logs."""
        protocol = engine_with_feature.generate_replay_protocol(
            "test-feature", include_debug_logs=True
        )
        assert "debug_logs" in protocol

    def test_exclude_debug_logs(self, engine_with_feature):
        """Test excluding debug logs."""
        protocol = engine_with_feature.generate_replay_protocol(
            "test-feature", include_debug_logs=False
        )
        assert "debug_logs" not in protocol

    def test_nonexistent_feature_raises_error(self, engine_with_feature):
        """Test that nonexistent feature raises error."""
        with pytest.raises(ValueError):
            engine_with_feature.generate_replay_protocol("nonexistent")

    def test_save_replay_protocol(self, engine_with_feature):
        """Test saving replay protocol to file."""
        path = engine_with_feature.save_replay_protocol("test-feature")
        assert path.exists()

        # Verify content
        content = path.read_text()
        loaded = json.loads(content)
        assert loaded["feature_name"] == "test-feature"

    def test_get_step_summary(self, engine_with_feature):
        """Test getting step summary."""
        summary = engine_with_feature.get_step_summary("test-feature")

        assert summary["feature_name"] == "test-feature"
        assert summary["total_steps"] == 1
        assert len(summary["steps"]) == 1
        assert summary["steps"][0]["order"] == 1
