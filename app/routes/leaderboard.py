from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.database import get_db
from app.models import User, Drink
from app.schemas import LeaderboardResponse, LeaderboardEntryResponse, UserRankResponse
from app.dependencies import get_current_user

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])
ML_PER_OZ = 29.5735


def get_leaderboard_query(db: Session):
    """Build leaderboard query with ranking by drink count then total ml volume."""
    subquery = db.query(
        Drink.user_id,
        func.count(Drink.id).label("drink_count"),
        func.coalesce(func.sum(Drink.quantity_oz * ML_PER_OZ), 0.0).label("total_volume_ml"),
        func.max(Drink.timestamp).label("last_drink")
    ).group_by(Drink.user_id).subquery()

    query = db.query(
        User.id,
        User.username,
        subquery.c.drink_count,
        subquery.c.total_volume_ml,
        subquery.c.last_drink
    ).join(
        subquery,
        User.id == subquery.c.user_id
    ).order_by(desc(subquery.c.drink_count), desc(subquery.c.total_volume_ml), desc(subquery.c.last_drink))

    return query


@router.get("/global", response_model=LeaderboardResponse)
def get_global_leaderboard(
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=500)
):
    """
    Get global leaderboard.
    
    Returns top users by drink count, with total logged volume in ml.
    """
    query = get_leaderboard_query(db)
    entries = query.limit(limit).all()

    leaderboard_entries = [
        LeaderboardEntryResponse(
            rank=idx + 1,
            user_id=entry.id,
            username=entry.username,
            drink_count=entry.drink_count or 0,
            total_volume_ml=float(entry.total_volume_ml) if entry.total_volume_ml else 0.0,
            last_drink_timestamp=entry.last_drink
        )
        for idx, entry in enumerate(entries)
    ]

    total_users = db.query(func.count(User.id)).scalar()

    return LeaderboardResponse(
        entries=leaderboard_entries,
        total_users=total_users
    )


@router.get("/my-rank", response_model=UserRankResponse)
def get_user_rank(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's rank with nearby competitors.
    
    Returns user's rank, drink count, total logged ml volume, and ±5 nearby users.
    """
    query = get_leaderboard_query(db)
    all_entries = query.all()

    # Find current user's position
    user_rank = None
    user_drink_count = None
    user_total_volume_ml = None

    for idx, entry in enumerate(all_entries):
        if entry.id == current_user.id:
            user_rank = idx + 1
            user_drink_count = entry.drink_count or 0
            user_total_volume_ml = float(entry.total_volume_ml) if entry.total_volume_ml else 0.0
            break

    if user_rank is None:
        # User has no drinks yet
        user_rank = len(all_entries) + 1
        user_drink_count = 0
        user_total_volume_ml = 0.0

    # Get nearby users (±5)
    start_idx = max(0, user_rank - 6)
    end_idx = min(len(all_entries), user_rank + 5)
    nearby = all_entries[start_idx:end_idx]

    nearby_entries = [
        LeaderboardEntryResponse(
            rank=start_idx + idx + 1,
            user_id=entry.id,
            username=entry.username,
            drink_count=entry.drink_count or 0,
            total_volume_ml=float(entry.total_volume_ml) if entry.total_volume_ml else 0.0,
            last_drink_timestamp=entry.last_drink
        )
        for idx, entry in enumerate(nearby)
    ]

    return UserRankResponse(
        rank=user_rank,
        drink_count=user_drink_count,
        total_volume_ml=user_total_volume_ml,
        nearby_users=nearby_entries
    )
