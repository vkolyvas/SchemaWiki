"""Pydantic schemas for feature request/response validation."""

from typing import Optional

from pydantic import BaseModel, Field


class FeatureCreate(BaseModel):
    """Schema for creating a new feature."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    version: str = Field(default="0.1.0", pattern=r"^\d+\.\d+\.\d+$")
    tags: Optional[list[str]] = None
    plan_content: Optional[str] = None


class FeatureUpdate(BaseModel):
    """Schema for updating a feature."""

    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern=r"^(planning|in_progress|completed)$")
    tags: Optional[list[str]] = None
    version: Optional[str] = Field(None, pattern=r"^\d+\.\d+\.\d+$")


class FeatureFileUpdate(BaseModel):
    """Schema for updating a feature file."""

    filename: str = Field(
        ...,
        pattern=r"^(plan\.md|implementation\.md|agent_steps\.yaml|architecture\.md|api_contracts\.yaml|tests\.md)$",
    )
    content: str
    commit_message: Optional[str] = None


class FeatureDependencyAdd(BaseModel):
    """Schema for adding a feature dependency."""

    to_feature: str = Field(..., min_length=1)
    dependency_type: str = Field(default="required", pattern=r"^(required|optional)$")


class FeatureVersionBump(BaseModel):
    """Schema for bumping feature version."""

    bump_type: str = Field(default="minor", pattern=r"^(major|minor|patch)$")


class FeatureResponse(BaseModel):
    """Schema for feature response."""

    name: str
    version: str
    description: Optional[str]
    status: str
    tags: list[str]
    dependencies: list[dict]
    created_at: Optional[str]
    updated_at: Optional[str]
    last_replay_commit: Optional[str]
    files: dict[str, str]
    file_paths: dict[str, str]
    debug_logs: list[dict]
    git_history: list[dict]


class FeatureListItem(BaseModel):
    """Schema for feature list item."""

    name: str
    version: str
    description: Optional[str]
    status: str
    tags: list[str]
    created_at: Optional[str]
    updated_at: Optional[str]


class SearchQuery(BaseModel):
    """Schema for search query."""

    q: str = Field(..., min_length=1)
    tags: Optional[list[str]] = None
    limit: int = Field(default=10, ge=1, le=100)


class HookEvent(BaseModel):
    """Schema for hook events."""

    event_type: str = Field(
        ...,
        pattern=r"^(feature_created|feature_updated|feature_deleted|build_started|build_failed|test_failed|deploy)$",
    )
    feature_name: Optional[str] = None
    payload: Optional[dict] = None


class ReplayRequest(BaseModel):
    """Schema for replay request."""

    version: Optional[str] = Field(None, pattern=r"^\d+\.\d+\.\d+$")
    include_debug_logs: bool = Field(default=False)
