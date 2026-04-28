from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.dependencies import get_current_user
from app.models import CommunityPost, Drink, User
from app.schemas import CommunityFeedResponse, CommunityPostResponse

router = APIRouter(prefix="/community", tags=["community"])

UPLOAD_DIR = Path("uploads/community")
ML_PER_OZ = 29.5735
MAX_IMAGE_SIZE_BYTES = 8 * 1024 * 1024


def _save_image_file(image: UploadFile) -> str:
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image files are allowed"
        )

    content = image.file.read()
    if len(content) > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image must be <= 8MB"
        )

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    ext = Path(image.filename or "").suffix or ".jpg"
    file_name = f"{uuid4().hex}{ext}"
    out_path = UPLOAD_DIR / file_name
    out_path.write_bytes(content)

    # Served by StaticFiles at /uploads
    return f"/uploads/community/{file_name}"


def _to_post_response(post: CommunityPost) -> CommunityPostResponse:
    drink_type_name = None
    drink_volume_ml = None

    if post.drink is not None:
        drink_volume_ml = round(float(post.drink.quantity_oz) * ML_PER_OZ, 1)
        if post.drink.drink_type is not None:
            drink_type_name = post.drink.drink_type.name

    return CommunityPostResponse(
        id=post.id,
        user_id=post.user_id,
        username=post.user.username,
        text=post.text,
        image_url=post.image_url,
        drink_id=post.drink_id,
        drink_type_name=drink_type_name,
        drink_volume_ml=drink_volume_ml,
        created_at=post.created_at,
    )


@router.post("/posts", response_model=CommunityPostResponse)
def create_community_post(
    text: str = Form(...),
    drink_id: int | None = Form(None),
    image: UploadFile | None = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a community post with text and optional image.
    """
    cleaned_text = (text or "").strip()
    if not cleaned_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post text cannot be empty"
        )

    linked_drink = None
    if drink_id is not None:
        linked_drink = db.query(Drink).filter(Drink.id == drink_id, Drink.user_id == current_user.id).first()
        if not linked_drink:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Drink entry not found for this user"
            )

    image_url = _save_image_file(image) if image else None

    post = CommunityPost(
        user_id=current_user.id,
        drink_id=drink_id,
        text=cleaned_text,
        image_url=image_url,
        created_at=datetime.utcnow(),
    )
    db.add(post)
    db.commit()
    db.refresh(post)

    post = db.query(CommunityPost).options(
        joinedload(CommunityPost.user),
        joinedload(CommunityPost.drink).joinedload(Drink.drink_type),
    ).filter(CommunityPost.id == post.id).first()

    return _to_post_response(post)


@router.get("/feed", response_model=CommunityFeedResponse)
def get_community_feed(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """
    Get latest community posts.
    """
    total = db.query(CommunityPost).count()
    posts = db.query(CommunityPost).options(
        joinedload(CommunityPost.user),
        joinedload(CommunityPost.drink).joinedload(Drink.drink_type),
    ).order_by(CommunityPost.created_at.desc()).offset(skip).limit(limit).all()

    return CommunityFeedResponse(
        total=total,
        page=skip // limit,
        limit=limit,
        posts=[_to_post_response(post) for post in posts]
    )
