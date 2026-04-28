from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from app.models import User, Drink, DrinkType
from app.schemas import (
    DrinkTypeResponse, DrinkLogRequest, DrinkResponse, DrinkHistoryResponse,
    DrinkLogResponse, CommunityPostPrompt
)
from app.dependencies import get_current_user

router = APIRouter(prefix="/drinks", tags=["drinks"])


@router.get("/types", response_model=list[DrinkTypeResponse])
def get_drink_types(db: Session = Depends(get_db)):
    """Get all predefined drink types."""
    drink_types = db.query(DrinkType).all()
    return drink_types


@router.post("/log", response_model=DrinkLogResponse)
def log_drink(
    drink_log: DrinkLogRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Log a drink for current user.
    
    Stores user-provided drink volume and metadata.
    """
    # Validate drink type exists
    drink_type = db.query(DrinkType).filter(
        DrinkType.id == drink_log.drink_type_id
    ).first()

    if not drink_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drink type not found"
        )

    # Validate quantity
    if drink_log.quantity_oz <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity must be greater than 0"
        )

    # Create drink record
    db_drink = Drink(
        user_id=current_user.id,
        drink_type_id=drink_log.drink_type_id,
        quantity_oz=drink_log.quantity_oz,
        # Kept for DB compatibility; not used in API or metrics.
        standard_drinks=0.0,
        timestamp=drink_log.timestamp or datetime.utcnow(),
        notes=drink_log.notes
    )

    db.add(db_drink)
    db.commit()
    db.refresh(db_drink)

    return DrinkLogResponse(
        drink=db_drink,
        community_prompt=CommunityPostPrompt(
            should_prompt=True,
            drink_id=db_drink.id,
            image_recommended=True,
            message="Want to share this in the community? Add text and optionally a photo."
        )
    )


@router.get("/my-history", response_model=DrinkHistoryResponse)
def get_drink_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    drink_type_id: int = Query(None),
    days: int = Query(None, ge=1)
):
    """
    Get current user's drink history with pagination and filters.
    
    Query params:
    - skip: Pagination offset (default 0)
    - limit: Number of results (default 20, max 100)
    - drink_type_id: Filter by drink type (optional)
    - days: Filter to last N days (optional)
    """
    query = db.query(Drink).filter(Drink.user_id == current_user.id)

    # Apply drink type filter
    if drink_type_id:
        query = query.filter(Drink.drink_type_id == drink_type_id)

    # Apply date range filter
    if days:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        query = query.filter(Drink.timestamp >= cutoff_date)

    # Get total count
    total = query.count()

    # Apply pagination and sort
    drinks = query.order_by(Drink.timestamp.desc()).offset(skip).limit(limit).all()

    return DrinkHistoryResponse(
        total=total,
        page=skip // limit,
        limit=limit,
        drinks=drinks
    )
