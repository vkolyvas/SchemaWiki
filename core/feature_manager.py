"""Feature management business logic."""

import re
from typing import Optional
from datetime import datetime

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from storage.metadata_db import Feature, FeatureTag, FeatureDependency
from storage.file_store import FileStore
from storage.git_repo import GitRepo


class FeatureManager:
    """Manage features with CRUD operations, versioning, and structured responses."""

    def __init__(self, db_session: AsyncSession):
        """Initialize feature manager with database session."""
        self.db = db_session
        self.file_store = FileStore()
        self.git_repo = GitRepo(str(self.file_store.base_path))

    async def create_feature(
        self,
        name: str,
        description: Optional[str] = None,
        version: str = "0.1.0",
        tags: Optional[list[str]] = None,
        plan_content: Optional[str] = None,
    ) -> dict:
        """Create a new feature with versioning."""
        # Check if feature already exists
        existing = await self.db.execute(
            select(Feature).where(Feature.name == name)
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"Feature '{name}' already exists")

        # Create feature directory
        self.file_store.create_feature_dir(name)

        # Write initial plan if provided
        if plan_content:
            self.file_store.write_file(name, FileStore.PLAN_FILE, plan_content)

        # Create database record
        feature = Feature(
            name=name,
            version=version,
            description=description,
            status="planning",
        )
        self.db.add(feature)
        await self.db.flush()

        # Add tags
        if tags:
            for tag in tags:
                tag_obj = FeatureTag(feature_id=feature.id, tag=tag)
                self.db.add(tag_obj)

        await self.db.commit()
        await self.db.refresh(feature)

        # Create git commit for the new feature
        commit_hash = self.git_repo.commit_feature_change(
            name,
            f"Create feature {name} v{version}"
        )

        # Update with commit hash
        feature.last_replay_commit = commit_hash
        await self.db.commit()

        return await self.get_feature(name)

    async def get_feature(self, name: str) -> dict:
        """Get feature with all metadata and file contents."""
        result = await self.db.execute(
            select(Feature)
            .options(selectinload(Feature.tags), selectinload(Feature.dependencies))
            .where(Feature.name == name)
        )
        feature = result.scalar_one_or_none()

        if not feature:
            raise ValueError(f"Feature '{name}' not found")

        # Get tags
        tags = [t.tag for t in feature.tags]

        # Get dependencies
        dependencies = []
        for dep in feature.dependencies:
            to_feature = await self.db.get(Feature, dep.to_feature_id)
            if to_feature:
                dependencies.append({
                    "name": to_feature.name,
                    "version": to_feature.version,
                    "type": dep.dependency_type,
                })

        # Get all files
        all_files = self.file_store.get_all_files(name)

        # Get debug logs
        debug_logs = self.file_store.get_debug_logs(name)

        # Get git history
        git_history = self.git_repo.get_commit_history(name)

        return self._build_feature_response(
            feature, tags, dependencies, all_files, debug_logs, git_history
        )

    async def update_feature(
        self,
        name: str,
        description: Optional[str] = None,
        status: Optional[str] = None,
        tags: Optional[list[str]] = None,
        version: Optional[str] = None,
    ) -> dict:
        """Update feature metadata."""
        result = await self.db.execute(
            select(Feature)
            .options(selectinload(Feature.tags))
            .where(Feature.name == name)
        )
        feature = result.scalar_one_or_none()

        if not feature:
            raise ValueError(f"Feature '{name}' not found")

        # Update fields
        if description is not None:
            feature.description = description
        if status is not None:
            feature.status = status
        if version is not None:
            feature.version = version

        # Update tags
        if tags is not None:
            # Remove existing tags
            await self.db.execute(
                delete(FeatureTag).where(FeatureTag.feature_id == feature.id)
            )
            # Add new tags
            for tag in tags:
                tag_obj = FeatureTag(feature_id=feature.id, tag=tag)
                self.db.add(tag_obj)

        feature.updated_at = datetime.now()
        await self.db.commit()
        await self.db.refresh(feature)

        return await self.get_feature(name)

    async def update_feature_file(
        self,
        name: str,
        filename: str,
        content: str,
        commit_message: Optional[str] = None,
    ) -> dict:
        """Update a feature file and create git commit."""
        if not self.file_store.feature_exists(name):
            raise ValueError(f"Feature '{name}' not found")

        # Write file
        self.file_store.write_file(name, filename, content)

        # Create git commit
        if commit_message is None:
            commit_message = f"Update {filename} for {name}"

        commit_hash = self.git_repo.commit_feature_change(name, commit_message, [filename])

        # Update feature's last replay commit if replay protocol changed
        if filename == FileStore.REPLAY_PROTOCOL_FILE:
            result = await self.db.execute(
                select(Feature).where(Feature.name == name)
            )
            feature = result.scalar_one()
            feature.last_replay_commit = commit_hash
            await self.db.commit()

        return await self.get_feature(name)

    async def delete_feature(self, name: str) -> None:
        """Delete a feature."""
        result = await self.db.execute(
            select(Feature).where(Feature.name == name)
        )
        feature = result.scalar_one_or_none()

        if not feature:
            raise ValueError(f"Feature '{name}' not found")

        # Delete from database (cascades to tags and dependencies)
        await self.db.delete(feature)
        await self.db.commit()

        # Delete files
        self.file_store.delete_feature(name)

    async def list_features(
        self,
        status: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> list[dict]:
        """List all features with optional filtering."""
        query = select(Feature).options(selectinload(Feature.tags))

        if status:
            query = query.where(Feature.status == status)

        if tag:
            query = query.join(FeatureTag).where(FeatureTag.tag == tag)

        result = await self.db.execute(query.order_by(Feature.updated_at.desc()))
        features = result.scalars().all()

        return [
            {
                "name": f.name,
                "version": f.version,
                "description": f.description,
                "status": f.status,
                "tags": [t.tag for t in f.tags],
                "created_at": f.created_at.isoformat() if f.created_at else None,
                "updated_at": f.updated_at.isoformat() if f.updated_at else None,
            }
            for f in features
        ]

    async def bump_version(
        self,
        name: str,
        bump_type: str = "minor",
    ) -> dict:
        """Bump feature version (major, minor, or patch)."""
        result = await self.db.execute(
            select(Feature).where(Feature.name == name)
        )
        feature = result.scalar_one_or_none()

        if not feature:
            raise ValueError(f"Feature '{name}' not found")

        # Parse current version
        version_parts = feature.version.split(".")
        if len(version_parts) != 3:
            version_parts = [0, 0, 0]

        major, minor, patch = map(int, version_parts)

        # Bump version
        if bump_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif bump_type == "minor":
            minor += 1
            patch = 0
        else:  # patch
            patch += 1

        new_version = f"{major}.{minor}.{patch}"
        feature.version = new_version
        await self.db.commit()

        return await self.get_feature(name)

    async def add_dependency(
        self,
        from_feature: str,
        to_feature: str,
        dependency_type: str = "required",
    ) -> dict:
        """Add a dependency between features."""
        # Get both features
        from_result = await self.db.execute(
            select(Feature).where(Feature.name == from_feature)
        )
        to_result = await self.db.execute(
            select(Feature).where(Feature.name == to_feature)
        )

        from_feat = from_result.scalar_one_or_none()
        to_feat = to_result.scalar_one_or_none()

        if not from_feat:
            raise ValueError(f"Feature '{from_feature}' not found")
        if not to_feat:
            raise ValueError(f"Feature '{to_feature}' not found")

        # Check if dependency already exists
        existing = await self.db.execute(
            select(FeatureDependency).where(
                FeatureDependency.from_feature_id == from_feat.id,
                FeatureDependency.to_feature_id == to_feat.id,
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"Dependency from '{from_feature}' to '{to_feature}' already exists")

        # Create dependency
        dep = FeatureDependency(
            from_feature_id=from_feat.id,
            to_feature_id=to_feat.id,
            dependency_type=dependency_type,
        )
        self.db.add(dep)
        await self.db.commit()

        return await self.get_feature(from_feature)

    def _build_feature_response(
        self,
        feature: Feature,
        tags: list[str],
        dependencies: list[dict],
        all_files: dict,
        debug_logs: list[dict],
        git_history: list[dict],
    ) -> dict:
        """Build a structured response for a feature."""
        return {
            "name": feature.name,
            "version": feature.version,
            "description": feature.description,
            "status": feature.status,
            "tags": tags,
            "dependencies": dependencies,
            "created_at": feature.created_at.isoformat() if feature.created_at else None,
            "updated_at": feature.updated_at.isoformat() if feature.updated_at else None,
            "last_replay_commit": feature.last_replay_commit,
            "files": {
                "plan": all_files.get(FileStore.PLAN_FILE, ""),
                "implementation": all_files.get(FileStore.IMPLEMENTATION_FILE, ""),
                "agent_steps": all_files.get(FileStore.AGENT_STEPS_FILE, ""),
                "replay_protocol": all_files.get(FileStore.REPLAY_PROTOCOL_FILE, ""),
                "architecture": all_files.get(FileStore.ARCHITECTURE_FILE, ""),
                "api_contracts": all_files.get(FileStore.API_CONTRACTS_FILE, ""),
                "tests": all_files.get(FileStore.TESTS_FILE, ""),
            },
            "file_paths": {
                "plan": str(self.file_store.get_feature_path(feature.name) / FileStore.PLAN_FILE),
                "implementation": str(self.file_store.get_feature_path(feature.name) / FileStore.IMPLEMENTATION_FILE),
                "agent_steps": str(self.file_store.get_feature_path(feature.name) / FileStore.AGENT_STEPS_FILE),
                "replay_protocol": str(self.file_store.get_feature_path(feature.name) / FileStore.REPLAY_PROTOCOL_FILE),
                "architecture": str(self.file_store.get_feature_path(feature.name) / FileStore.ARCHITECTURE_FILE),
                "api_contracts": str(self.file_store.get_feature_path(feature.name) / FileStore.API_CONTRACTS_FILE),
                "tests": str(self.file_store.get_feature_path(feature.name) / FileStore.TESTS_FILE),
            },
            "debug_logs": debug_logs,
            "git_history": git_history,
        }
