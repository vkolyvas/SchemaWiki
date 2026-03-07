"""Feature CRUD endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.feature_manager import FeatureManager
from core.replay_engine import ReplayEngine
from schemas import (
    FeatureCreate,
    FeatureDependencyAdd,
    FeatureFileUpdate,
    FeatureListItem,
    FeatureResponse,
    FeatureUpdate,
    FeatureVersionBump,
)
from storage import get_db

router = APIRouter(prefix="/features", tags=["features"])


async def get_feature_manager(db: AsyncSession = Depends(get_db)) -> FeatureManager:
    """Get feature manager instance."""
    return FeatureManager(db)


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_feature(
    feature_data: FeatureCreate,
    fm: FeatureManager = Depends(get_feature_manager),
):
    """Create a new feature."""
    try:
        return await fm.create_feature(
            name=feature_data.name,
            description=feature_data.description,
            version=feature_data.version,
            tags=feature_data.tags,
            plan_content=feature_data.plan_content,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{name}", response_model=dict)
async def get_feature(
    name: str,
    fm: FeatureManager = Depends(get_feature_manager),
):
    """Get feature by name."""
    try:
        return await fm.get_feature(name)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("", response_model=list[FeatureListItem])
async def list_features(
    status: Optional[str] = None,
    tag: Optional[str] = None,
    fm: FeatureManager = Depends(get_feature_manager),
):
    """List all features with optional filtering."""
    return await fm.list_features(status=status, tag=tag)


@router.patch("/{name}", response_model=dict)
async def update_feature(
    name: str,
    feature_data: FeatureUpdate,
    fm: FeatureManager = Depends(get_feature_manager),
):
    """Update feature metadata."""
    try:
        return await fm.update_feature(
            name=name,
            description=feature_data.description,
            status=feature_data.status,
            tags=feature_data.tags,
            version=feature_data.version,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feature(
    name: str,
    fm: FeatureManager = Depends(get_feature_manager),
):
    """Delete a feature."""
    try:
        await fm.delete_feature(name)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{name}/files", response_model=dict)
async def update_feature_file(
    name: str,
    file_data: FeatureFileUpdate,
    fm: FeatureManager = Depends(get_feature_manager),
):
    """Update a feature file."""
    try:
        return await fm.update_feature_file(
            name=name,
            filename=file_data.filename,
            content=file_data.content,
            commit_message=file_data.commit_message,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{name}/version/bump", response_model=dict)
async def bump_version(
    name: str,
    bump_data: FeatureVersionBump,
    fm: FeatureManager = Depends(get_feature_manager),
):
    """Bump feature version."""
    try:
        return await fm.bump_version(name=name, bump_type=bump_data.bump_type)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{name}/dependencies", response_model=dict)
async def add_dependency(
    name: str,
    dep_data: FeatureDependencyAdd,
    fm: FeatureManager = Depends(get_feature_manager),
):
    """Add a dependency to a feature."""
    try:
        return await fm.add_dependency(
            from_feature=name,
            to_feature=dep_data.to_feature,
            dependency_type=dep_data.dependency_type,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{name}/replay")
async def get_replay_protocol(
    name: str,
    include_debug_logs: bool = True,
):
    """Get replay protocol for a feature."""
    replay_engine = ReplayEngine()
    try:
        return replay_engine.generate_replay_protocol(name, include_debug_logs=include_debug_logs)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{name}/replay/generate")
async def generate_replay_protocol(
    name: str,
    include_debug_logs: bool = True,
):
    """Generate and save replay protocol for a feature."""
    replay_engine = ReplayEngine()
    try:
        path = replay_engine.save_replay_protocol(name, include_debug_logs=include_debug_logs)
        return {"status": "generated", "file_path": str(path)}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
