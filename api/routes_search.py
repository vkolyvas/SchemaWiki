"""Search endpoints for features."""

import re

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from storage import Feature, FeatureTag, get_db
from storage.file_store import FileStore

router = APIRouter(prefix="/search", tags=["search"])


@router.get("")
async def search_features(
    q: str = Query(..., min_length=1),
    tags: str = Query(None),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Search features by query string."""
    file_store = FileStore()

    # Parse tags from query string if provided
    tag_list = tags.split(",") if tags else None

    # Base query with eager loading
    query = select(Feature).options(selectinload(Feature.tags))

    # Filter by tags if provided
    if tag_list:
        query = query.join(FeatureTag).where(FeatureTag.tag.in_(tag_list))

    result = await db.execute(query.order_by(Feature.updated_at.desc()))
    features = result.scalars().all()

    # Search in feature names, descriptions, and file contents
    search_results = []
    q_lower = q.lower()

    for feature in features:
        # Check name and description
        name_match = q_lower in feature.name.lower()
        desc_match = feature.description and q_lower in feature.description.lower()

        # Check file contents
        file_match = False
        file_store_content = ""

        if file_store.feature_exists(feature.name):
            all_files = file_store.get_all_files(feature.name)
            for filename, content in all_files.items():
                if content and q_lower in content.lower():
                    file_match = True
                    file_store_content = content[:500]  # Preview
                    break

        if name_match or desc_match or file_match:
            search_results.append(
                {
                    "name": feature.name,
                    "version": feature.version,
                    "description": feature.description,
                    "status": feature.status,
                    "tags": [t.tag for t in feature.tags],
                    "match_type": (
                        "name" if name_match else ("description" if desc_match else "content")
                    ),
                    "preview": (
                        file_store_content
                        if file_match
                        else (feature.description[:200] if feature.description else None)
                    ),
                }
            )

        if len(search_results) >= limit:
            break

    return {
        "query": q,
        "total": len(search_results),
        "results": search_results,
    }


@router.get("/tags")
async def get_all_tags(db: AsyncSession = Depends(get_db)):
    """Get all unique tags."""
    result = await db.execute(select(FeatureTag.tag).distinct())
    tags = [row[0] for row in result.all()]
    return {"tags": tags}


@router.get("/semantic")
async def semantic_search(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=100),
):
    """Semantic search using embeddings (placeholder - requires Phase 4)."""
    # This requires sentence-transformers integration (Phase 4)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Semantic search requires vector embeddings (Phase 4)",
    )
