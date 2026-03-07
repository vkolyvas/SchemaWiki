"""Development event hooks."""

import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from storage import get_db, Feature
from storage.file_store import FileStore
from sqlalchemy import select

router = APIRouter(prefix="/hooks", tags=["hooks"])


@router.post("")
async def receive_hook(
    event_type: str,
    feature_name: str = None,
    payload: dict = None,
    db: AsyncSession = Depends(get_db),
):
    """Record development events."""
    valid_events = [
        "feature_created",
        "feature_updated",
        "feature_deleted",
        "build_started",
        "build_failed",
        "test_failed",
        "deploy",
    ]

    if event_type not in valid_events:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid event type. Must be one of: {valid_events}"
        )

    response = {
        "event_type": event_type,
        "feature_name": feature_name,
        "received": True,
    }

    # Process specific events
    if event_type == "feature_created":
        # Verify feature exists
        result = await db.execute(
            select(Feature).where(Feature.name == feature_name)
        )
        feature = result.scalar_one_or_none()
        if not feature:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feature '{feature_name}' not found"
            )
        response["message"] = f"Event recorded for feature '{feature_name}'"

    elif event_type == "build_failed" or event_type == "test_failed":
        # Store debug logs if feature provided
        if feature_name:
            file_store = FileStore()
            if file_store.feature_exists(feature_name):
                # Find the next attempt number
                existing_logs = file_store.get_debug_logs(feature_name)
                attempt_number = len(existing_logs) + 1

                # Create debug log content
                log_content = json.dumps({
                    "event_type": event_type,
                    "payload": payload or {},
                }, indent=2)

                file_store.add_debug_log(feature_name, attempt_number, log_content)
                response["debug_log_attempt"] = attempt_number

    elif event_type == "deploy":
        if feature_name:
            # Update feature status to completed
            result = await db.execute(
                select(Feature).where(Feature.name == feature_name)
            )
            feature = result.scalar_one_or_none()
            if feature:
                feature.status = "completed"
                await db.commit()
                response["feature_status"] = "completed"

    return response


@router.get("/events")
async def list_events():
    """List valid event types."""
    return {
        "event_types": [
            "feature_created",
            "feature_updated",
            "feature_deleted",
            "build_started",
            "build_failed",
            "test_failed",
            "deploy",
        ]
    }
