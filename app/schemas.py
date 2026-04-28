from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class TokenResponse(BaseModel):
    """Token response."""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"


class UserCreate(BaseModel):
    """User creation schema."""
    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response schema."""
    id: int
    username: str
    email: str
    created_at: datetime
    drink_count: int = 0
    total_volume_ml: float = 0.0
    rank: Optional[int] = None

    class Config:
        from_attributes = True


class DrinkTypeResponse(BaseModel):
    """Drink type response."""
    id: int
    name: str
    abv_percent: float
    standard_oz_per_serving: float

    class Config:
        from_attributes = True


class DrinkLogRequest(BaseModel):
    """Drink logging request."""
    drink_type_id: int
    quantity_oz: float
    timestamp: Optional[datetime] = None
    notes: Optional[str] = None


class DrinkResponse(BaseModel):
    """Drink response."""
    id: int
    user_id: int
    drink_type_id: int
    quantity_oz: float
    timestamp: datetime
    notes: Optional[str] = None
    drink_type: DrinkTypeResponse

    class Config:
        from_attributes = True


class CommunityPostPrompt(BaseModel):
    """Prompt metadata sent after logging a drink."""
    should_prompt: bool = True
    drink_id: int
    image_recommended: bool = True
    message: str


class DrinkLogResponse(BaseModel):
    """Drink log response with optional community prompt."""
    drink: DrinkResponse
    community_prompt: CommunityPostPrompt


class DrinkHistoryResponse(BaseModel):
    """Drink history with pagination."""
    total: int
    page: int
    limit: int
    drinks: list[DrinkResponse]


class LeaderboardEntryResponse(BaseModel):
    """Leaderboard entry."""
    rank: int
    user_id: int
    username: str
    drink_count: int
    total_volume_ml: float
    last_drink_timestamp: Optional[datetime] = None


class LeaderboardResponse(BaseModel):
    """Leaderboard response."""
    entries: list[LeaderboardEntryResponse]
    total_users: int


class UserRankResponse(BaseModel):
    """User rank response with context."""
    rank: int
    drink_count: int
    total_volume_ml: float
    nearby_users: list[LeaderboardEntryResponse]


class CommunityPostResponse(BaseModel):
    """Community post response."""
    id: int
    user_id: int
    username: str
    text: str
    image_url: Optional[str] = None
    drink_id: Optional[int] = None
    drink_type_name: Optional[str] = None
    drink_volume_ml: Optional[float] = None
    created_at: datetime


class CommunityFeedResponse(BaseModel):
    """Community feed with pagination."""
    total: int
    page: int
    limit: int
    posts: list[CommunityPostResponse]
