"""Database models and connection for SchemaWiki."""

import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime, timezone


def utc_now():
    """Return current UTC time."""
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class Feature(Base):
    """Feature model representing a documented feature."""
    __tablename__ = "features"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    version = Column(String(20), nullable=False, default="0.1.0")
    description = Column(Text, nullable=True)
    status = Column(String(50), default="planning")  # planning, in_progress, completed
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    last_replay_commit = Column(String(40), nullable=True)

    tags = relationship("FeatureTag", back_populates="feature", cascade="all, delete-orphan")
    dependencies = relationship(
        "FeatureDependency",
        foreign_keys="FeatureDependency.from_feature_id",
        back_populates="from_feature",
        cascade="all, delete-orphan"
    )


class FeatureTag(Base):
    """Tags associated with features."""
    __tablename__ = "feature_tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    feature_id = Column(Integer, ForeignKey("features.id", ondelete="CASCADE"), nullable=False)
    tag = Column(String(100), nullable=False)

    feature = relationship("Feature", back_populates="tags")


class FeatureDependency(Base):
    """Dependencies between features."""
    __tablename__ = "feature_dependencies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    from_feature_id = Column(Integer, ForeignKey("features.id", ondelete="CASCADE"), nullable=False)
    to_feature_id = Column(Integer, ForeignKey("features.id", ondelete="CASCADE"), nullable=False)
    dependency_type = Column(String(50), default="required")  # required, optional

    from_feature = relationship("Feature", foreign_keys=[from_feature_id], back_populates="dependencies")
    to_feature = relationship("Feature", foreign_keys=[to_feature_id])


# Database engine and session maker
_engine = None
_session_factory = None


def get_database_url() -> str:
    """Get database URL from environment or use default."""
    return os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://schemawiki:schemawiki@localhost:5433/schemawiki"
    )


def get_features_data_path() -> str:
    """Get features data path from environment."""
    return os.getenv("FEATURES_DATA_PATH", "/data/features")


async def init_db() -> None:
    """Initialize database engine and create tables."""
    global _engine, _session_factory

    if _engine is None:
        _engine = create_async_engine(get_database_url(), echo=False)
        _session_factory = async_sessionmaker(
            _engine, class_=AsyncSession, expire_on_commit=False
        )

    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    global _session_factory

    if _session_factory is None:
        await init_db()

    async with _session_factory() as session:
        yield session


async def close_db() -> None:
    """Close database connection."""
    global _engine

    if _engine:
        await _engine.dispose()
        _engine = None
