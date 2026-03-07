"""Tests for file storage."""

import os
import tempfile

import pytest

from storage.file_store import FileStore


class TestFileStore:
    """Tests for FileStore."""

    @pytest.fixture
    def temp_store(self):
        """Create a temporary file store."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = FileStore(tmpdir)
            yield store

    def test_create_feature_dir(self, temp_store):
        """Test creating a feature directory."""
        path = temp_store.create_feature_dir("test-feature")
        assert path.exists()
        assert path.is_dir()

    def test_feature_exists(self, temp_store):
        """Test checking if feature exists."""
        assert not temp_store.feature_exists("test-feature")
        temp_store.create_feature_dir("test-feature")
        assert temp_store.feature_exists("test-feature")

    def test_get_feature_path(self, temp_store):
        """Test getting feature path."""
        path = temp_store.get_feature_path("test-feature")
        assert "test-feature" in str(path)

    def test_write_and_read_file(self, temp_store):
        """Test writing and reading files."""
        temp_store.create_feature_dir("test-feature")
        temp_store.write_file("test-feature", "test.txt", "Hello World")
        content = temp_store.read_file("test-feature", "test.txt")
        assert content == "Hello World"

    def test_read_nonexistent_file(self, temp_store):
        """Test reading nonexistent file returns None."""
        content = temp_store.read_file("test-feature", "test.txt")
        assert content is None

    def test_delete_feature(self, temp_store):
        """Test deleting a feature."""
        temp_store.create_feature_dir("test-feature")
        assert temp_store.feature_exists("test-feature")
        temp_store.delete_feature("test-feature")
        assert not temp_store.feature_exists("test-feature")

    def test_list_features(self, temp_store):
        """Test listing features."""
        temp_store.create_feature_dir("feature-1")
        temp_store.create_feature_dir("feature-2")
        features = temp_store.list_features()
        assert "feature-1" in features
        assert "feature-2" in features

    def test_get_all_files(self, temp_store):
        """Test getting all feature files."""
        temp_store.create_feature_dir("test-feature")
        temp_store.write_file("test-feature", "plan.md", "# Plan")
        files = temp_store.get_all_files("test-feature")
        assert "plan.md" in files
        assert files["plan.md"] == "# Plan"

    def test_write_replay_protocol(self, temp_store):
        """Test writing replay protocol."""
        temp_store.create_feature_dir("test-feature")
        protocol = {"version": "1.0", "steps": []}
        path = temp_store.write_replay_protocol("test-feature", protocol)
        assert path.exists()

        # Read back
        loaded = temp_store.read_replay_protocol("test-feature")
        assert loaded == protocol

    def test_write_agent_steps(self, temp_store):
        """Test writing agent steps."""
        temp_store.create_feature_dir("test-feature")
        steps = [
            {"order": 1, "description": "Step 1", "command": "echo hello"},
            {"order": 2, "description": "Step 2", "command": "echo world"},
        ]
        path = temp_store.write_agent_steps("test-feature", steps)
        assert path.exists()

        # Read back
        loaded = temp_store.read_agent_steps("test-feature")
        assert len(loaded) == 2
        assert loaded[0]["order"] == 1

    def test_debug_logs(self, temp_store):
        """Test debug logs."""
        temp_store.create_feature_dir("test-feature")

        # Add debug log
        log_path = temp_store.add_debug_log("test-feature", 1, "Error: something failed")
        assert log_path.exists()

        # Get debug logs
        logs = temp_store.get_debug_logs("test-feature")
        assert len(logs) == 1
        assert logs[0]["attempt"] == 1

    def test_sanitize_feature_name(self, temp_store):
        """Test feature name sanitization."""
        # Create feature with special characters
        path = temp_store.get_feature_path("my@#$feature!")
        # Should not crash
        assert "my" in str(path)
