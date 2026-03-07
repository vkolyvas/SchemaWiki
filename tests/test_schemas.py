"""Tests for SchemaWiki schemas."""

import pytest
from pydantic import ValidationError

from schemas.feature_schema import (
    FeatureCreate,
    FeatureDependencyAdd,
    FeatureFileUpdate,
    FeatureUpdate,
    FeatureVersionBump,
    HookEvent,
    ReplayRequest,
    SearchQuery,
)


class TestFeatureCreate:
    """Tests for FeatureCreate schema."""

    def test_valid_feature_create(self):
        """Test creating a valid feature."""
        feature = FeatureCreate(name="test-feature")
        assert feature.name == "test-feature"
        assert feature.version == "0.1.0"

    def test_feature_with_description(self):
        """Test creating feature with description."""
        feature = FeatureCreate(name="test-feature", description="A test feature")
        assert feature.description == "A test feature"

    def test_feature_with_tags(self):
        """Test creating feature with tags."""
        feature = FeatureCreate(name="test-feature", tags=["auth", "security"])
        assert feature.tags == ["auth", "security"]

    def test_feature_with_custom_version(self):
        """Test creating feature with custom version."""
        feature = FeatureCreate(name="test-feature", version="1.2.3")
        assert feature.version == "1.2.3"

    def test_invalid_version(self):
        """Test that invalid version is rejected."""
        with pytest.raises(ValidationError):
            FeatureCreate(name="test", version="invalid")

    def test_empty_name_rejected(self):
        """Test that empty name is rejected."""
        with pytest.raises(ValidationError):
            FeatureCreate(name="")


class TestFeatureUpdate:
    """Tests for FeatureUpdate schema."""

    def test_valid_update(self):
        """Test valid feature update."""
        update = FeatureUpdate(description="Updated description")
        assert update.description == "Updated description"

    def test_valid_status_values(self):
        """Test valid status values."""
        for status in ["planning", "in_progress", "completed"]:
            update = FeatureUpdate(status=status)
            assert update.status == status

    def test_invalid_status_rejected(self):
        """Test that invalid status is rejected."""
        with pytest.raises(ValidationError):
            FeatureUpdate(status="invalid")


class TestFeatureFileUpdate:
    """Tests for FeatureFileUpdate schema."""

    def test_valid_filename(self):
        """Test valid filename."""
        file_update = FeatureFileUpdate(filename="plan.md", content="# Plan")
        assert file_update.filename == "plan.md"

    def test_all_valid_filenames(self):
        """Test all valid filenames."""
        valid_files = [
            "plan.md",
            "implementation.md",
            "agent_steps.yaml",
            "architecture.md",
            "api_contracts.yaml",
            "tests.md",
        ]
        for filename in valid_files:
            file_update = FeatureFileUpdate(filename=filename, content="")
            assert file_update.filename == filename

    def test_invalid_filename_rejected(self):
        """Test that invalid filename is rejected."""
        with pytest.raises(ValidationError):
            FeatureFileUpdate(filename="invalid.txt", content="")


class TestFeatureDependencyAdd:
    """Tests for FeatureDependencyAdd schema."""

    def test_valid_dependency(self):
        """Test valid dependency."""
        dep = FeatureDependencyAdd(to_feature="feature-b")
        assert dep.to_feature == "feature-b"
        assert dep.dependency_type == "required"

    def test_optional_dependency(self):
        """Test optional dependency."""
        dep = FeatureDependencyAdd(to_feature="feature-b", dependency_type="optional")
        assert dep.dependency_type == "optional"


class TestFeatureVersionBump:
    """Tests for FeatureVersionBump schema."""

    def test_valid_bump_types(self):
        """Test valid bump types."""
        for bump_type in ["major", "minor", "patch"]:
            bump = FeatureVersionBump(bump_type=bump_type)
            assert bump.bump_type == bump_type


class TestSearchQuery:
    """Tests for SearchQuery schema."""

    def test_valid_search(self):
        """Test valid search query."""
        search = SearchQuery(q="test")
        assert search.q == "test"
        assert search.limit == 10

    def test_custom_limit(self):
        """Test custom limit."""
        search = SearchQuery(q="test", limit=50)
        assert search.limit == 50

    def test_empty_query_rejected(self):
        """Test that empty query is rejected."""
        with pytest.raises(ValidationError):
            SearchQuery(q="")


class TestHookEvent:
    """Tests for HookEvent schema."""

    def test_valid_event_types(self):
        """Test valid event types."""
        valid_events = [
            "feature_created",
            "feature_updated",
            "feature_deleted",
            "build_started",
            "build_failed",
            "test_failed",
            "deploy",
        ]
        for event in valid_events:
            hook = HookEvent(event_type=event)
            assert hook.event_type == event


class TestReplayRequest:
    """Tests for ReplayRequest schema."""

    def test_default_values(self):
        """Test default values."""
        replay = ReplayRequest()
        assert replay.include_debug_logs is False

    def test_with_version(self):
        """Test with version."""
        replay = ReplayRequest(version="1.0.0")
        assert replay.version == "1.0.0"
