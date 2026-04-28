from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    """User model."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    drinks = relationship("Drink", back_populates="user")
    community_posts = relationship("CommunityPost", back_populates="user")

    def __repr__(self):
        return f"<User {self.username}>"


class DrinkType(Base):
    """Predefined drink type (Beer, Wine, etc.)."""
    __tablename__ = "drink_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    abv_percent = Column(Float, nullable=False)  # Alcohol by volume %
    standard_oz_per_serving = Column(Float, nullable=False)  # Standard serving size in oz

    drinks = relationship("Drink", back_populates="drink_type")

    def __repr__(self):
        return f"<DrinkType {self.name}>"


class Drink(Base):
    """Logged drink entry."""
    __tablename__ = "drinks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    drink_type_id = Column(Integer, ForeignKey("drink_types.id"), nullable=False)
    quantity_oz = Column(Float, nullable=False)  # Quantity in ounces
    standard_drinks = Column(Numeric(5, 2), nullable=False)  # Calculated standard drinks
    timestamp = Column(DateTime, default=datetime.utcnow)
    party_id = Column(Integer, nullable=True)  # Future: reference to party
    notes = Column(String, nullable=True)

    user = relationship("User", back_populates="drinks")
    drink_type = relationship("DrinkType", back_populates="drinks")
    community_posts = relationship("CommunityPost", back_populates="drink")

    def __repr__(self):
        return f"<Drink {self.user_id} - {self.drink_type_id}>"


class CommunityPost(Base):
    """Community post created by users after drink logs."""
    __tablename__ = "community_posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    drink_id = Column(Integer, ForeignKey("drinks.id"), nullable=True)
    text = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="community_posts")
    drink = relationship("Drink", back_populates="community_posts")

    def __repr__(self):
        return f"<CommunityPost {self.id} user={self.user_id}>"
