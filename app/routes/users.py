from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from app.database import get_db
from app.models import User, Drink
from app.schemas import UserResponse
from app.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])
ML_PER_OZ = 29.5735


def calculate_user_stats(user_id: int, db: Session):
    """Calculate drink count, total volume (ml), and rank for a user."""
    user_stats_subquery = db.query(
        User.id.label("user_id"),
        func.count(Drink.id).label("drink_count"),
        func.coalesce(func.sum(Drink.quantity_oz * ML_PER_OZ), 0.0).label("total_volume_ml")
    ).outerjoin(
        Drink, Drink.user_id == User.id
    ).group_by(
        User.id
    ).subquery()

    result = db.query(
        user_stats_subquery.c.drink_count,
        user_stats_subquery.c.total_volume_ml
    ).filter(
        user_stats_subquery.c.user_id == user_id
    ).first()

    drink_count = int(result.drink_count) if result else 0
    total_volume_ml = float(result.total_volume_ml) if result else 0.0

    # Rank by drink count first, then total ml volume as tiebreaker.
    higher_users_count = db.query(func.count()).select_from(user_stats_subquery).filter(
        or_(
            user_stats_subquery.c.drink_count > drink_count,
            and_(
                user_stats_subquery.c.drink_count == drink_count,
                user_stats_subquery.c.total_volume_ml > total_volume_ml
            )
        )
    ).scalar()

    rank = (higher_users_count or 0) + 1

    return drink_count, total_volume_ml, rank


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current user profile with stats."""
    drink_count, total_volume_ml, rank = calculate_user_stats(current_user.id, db)

    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        created_at=current_user.created_at,
        drink_count=drink_count,
        total_volume_ml=total_volume_ml,
        rank=rank
    )


@router.get("/{user_id}", response_model=UserResponse)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """Get public user profile."""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    drink_count, total_volume_ml, rank = calculate_user_stats(user_id, db)

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        created_at=user.created_at,
        drink_count=drink_count,
        total_volume_ml=total_volume_ml,
        rank=rank
    )
