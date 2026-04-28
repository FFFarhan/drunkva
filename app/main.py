from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import Base, engine
from app.routes import auth, users, drinks, leaderboard, community
from app.models import User, DrinkType, Drink, CommunityPost
from app.config import CORS_ORIGINS
import os

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DrunkVa API",
    description="Strava for drinking - track drinks and compete on leaderboards",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static uploads for community images
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(drinks.router)
app.include_router(leaderboard.router)
app.include_router(community.router)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.on_event("startup")
def startup_event():
    """Initialize database with comprehensive drink types on startup."""
    from sqlalchemy.orm import Session
    from app.database import SessionLocal

    db = SessionLocal()

    try:
        # Check if drink types already exist
        existing_types = db.query(DrinkType).count()

        if existing_types == 0:
            # Comprehensive seed with Indian & Global drinks
            default_drinks = [
                # POPULAR COMMERCIAL INDIAN SPIRITS
                DrinkType(name="Old Monk Rum", abv_percent=37.5, standard_oz_per_serving=1.5),
                DrinkType(name="Royal Challenge Whiskey", abv_percent=42.8, standard_oz_per_serving=1.5),
                DrinkType(name="Johnnie Walker Red Label", abv_percent=40.0, standard_oz_per_serving=1.5),
                DrinkType(name="McDowell's No. 1 Whiskey", abv_percent=42.8, standard_oz_per_serving=1.5),
                DrinkType(name="Bacardi Rum", abv_percent=37.5, standard_oz_per_serving=1.5),
                DrinkType(name="Solan No. 1 Whisky", abv_percent=42.8, standard_oz_per_serving=1.5),
                
                # INDIAN BEER - COMMERCIAL
                DrinkType(name="Kingfisher Beer", abv_percent=4.2, standard_oz_per_serving=12.0),
                DrinkType(name="Kingfisher Strong", abv_percent=8.0, standard_oz_per_serving=12.0),
                DrinkType(name="Tuborg Beer", abv_percent=4.8, standard_oz_per_serving=12.0),
                DrinkType(name="Carlsberg Beer", abv_percent=4.6, standard_oz_per_serving=12.0),
                DrinkType(name="Cobra Beer", abv_percent=4.0, standard_oz_per_serving=12.0),
                DrinkType(name="Thunderbolt Beer", abv_percent=7.2, standard_oz_per_serving=12.0),
                DrinkType(name="Haywards 5000", abv_percent=8.0, standard_oz_per_serving=12.0),
                DrinkType(name="Kalyani Black Label", abv_percent=5.0, standard_oz_per_serving=12.0),
                DrinkType(name="Bira 91", abv_percent=4.2, standard_oz_per_serving=11.0),
                DrinkType(name="Lion Beer", abv_percent=4.5, standard_oz_per_serving=12.0),
                
                # GOA REGION
                DrinkType(name="Cashew Feni", abv_percent=42.0, standard_oz_per_serving=2.0),
                DrinkType(name="Coconut Feni (Maddel)", abv_percent=42.8, standard_oz_per_serving=2.0),
                DrinkType(name="Urrak (Goan Palm Wine)", abv_percent=15.0, standard_oz_per_serving=5.0),
                DrinkType(name="Cazulo/Cajulo", abv_percent=41.0, standard_oz_per_serving=2.0),
                
                # NORTHEAST REGION
                DrinkType(name="Apong (Arunachal Pradesh)", abv_percent=12.0, standard_oz_per_serving=6.0),
                DrinkType(name="Handia/Hadia (Tribal Beer)", abv_percent=10.0, standard_oz_per_serving=8.0),
                DrinkType(name="Chhaang (Sikkim/Darjeeling)", abv_percent=10.0, standard_oz_per_serving=6.0),
                DrinkType(name="Chuak (Tripura)", abv_percent=10.0, standard_oz_per_serving=6.0),
                DrinkType(name="Chang (Ladakh)", abv_percent=6.0, standard_oz_per_serving=5.0),
                DrinkType(name="Rice Beer/Sura (Tribal)", abv_percent=12.0, standard_oz_per_serving=6.0),
                
                # SOUTH INDIA REGION
                DrinkType(name="Kallu (Kerala)", abv_percent=12.0, standard_oz_per_serving=6.0),
                DrinkType(name="Neera/Toddy (Kerala/Karnataka)", abv_percent=6.0, standard_oz_per_serving=8.0),
                
                # CENTRAL & WESTERN REGION
                DrinkType(name="Mahua Liquor (Chhattisgarh/MP)", abv_percent=35.0, standard_oz_per_serving=2.0),
                DrinkType(name="Mahua Daru (Tribal)", abv_percent=38.0, standard_oz_per_serving=2.0),
                DrinkType(name="Date Palm Toddy (MP)", abv_percent=5.0, standard_oz_per_serving=8.0),
                DrinkType(name="Sulfi Tree Sap (MP Tribal)", abv_percent=10.0, standard_oz_per_serving=6.0),
                
                # TAMIL NADU (TASMAC)
                DrinkType(name="Samrakshan (TASMAC TN)", abv_percent=42.8, standard_oz_per_serving=1.5),
                DrinkType(name="Kanya Brandy (TN)", abv_percent=42.8, standard_oz_per_serving=1.5),
                
                # Indian Wine
                DrinkType(name="Sula Wines (Red)", abv_percent=13.0, standard_oz_per_serving=5.0),
                DrinkType(name="Grover Zampa Cabernet", abv_percent=13.5, standard_oz_per_serving=5.0),
                
                # BANGALORE REGION - Student Favorites & Local Drinks
                DrinkType(name="Kingfisher Premium (Bangalore)", abv_percent=4.2, standard_oz_per_serving=12.0),
                DrinkType(name="Bira 91 (Bangalore Craft)", abv_percent=4.2, standard_oz_per_serving=11.0),
                DrinkType(name="Tuborg (Budget Beer)", abv_percent=4.8, standard_oz_per_serving=12.0),
                DrinkType(name="Bangalore Blonde (Local Brewery)", abv_percent=5.0, standard_oz_per_serving=12.0),
                DrinkType(name="UB City (UB Lime Beer)", abv_percent=4.5, standard_oz_per_serving=12.0),
                DrinkType(name="Simba Stout (Bangalore)", abv_percent=7.5, standard_oz_per_serving=12.0),
                DrinkType(name="Haywards Black (Premium)", abv_percent=8.0, standard_oz_per_serving=12.0),
                DrinkType(name="Sula White Wine (Bangalore)", abv_percent=13.0, standard_oz_per_serving=5.0),
                DrinkType(name="Student Favorite - Vodka Shot", abv_percent=40.0, standard_oz_per_serving=1.5),
                DrinkType(name="Bacardi Breezer (Student Mix)", abv_percent=4.8, standard_oz_per_serving=12.0),
                
                # MUMBAI REGION - Student Favorites & Local Drinks
                DrinkType(name="Kingfisher Strong (Mumbai)", abv_percent=8.0, standard_oz_per_serving=12.0),
                DrinkType(name="Haywards 5000 (Student Favorite)", abv_percent=8.0, standard_oz_per_serving=12.0),
                DrinkType(name="Tuborg Premium (Mumbai)", abv_percent=4.8, standard_oz_per_serving=12.0),
                DrinkType(name="Carlsberg Strong (Maharashtra)", abv_percent=7.5, standard_oz_per_serving=12.0),
                DrinkType(name="Godfather (Whiskey Blend)", abv_percent=40.0, standard_oz_per_serving=1.5),
                DrinkType(name="Imperial Blue Whiskey", abv_percent=42.8, standard_oz_per_serving=1.5),
                DrinkType(name="Officer's Choice Whiskey", abv_percent=42.8, standard_oz_per_serving=1.5),
                DrinkType(name="Goa Feni (Mumbai/Goa)", abv_percent=42.0, standard_oz_per_serving=2.0),
                DrinkType(name="Maharashtra Malt (Local)", abv_percent=40.0, standard_oz_per_serving=1.5),
                DrinkType(name="Student Party Mix (Rum+Cola)", abv_percent=35.0, standard_oz_per_serving=2.0),
                
                # BUDGET STUDENT DRINKS (Affordable for Testing Crowd)
                DrinkType(name="UB40 Malt (Ultra Budget)", abv_percent=4.0, standard_oz_per_serving=12.0),
                DrinkType(name="Bullets Whiskey (Cheap)", abv_percent=40.0, standard_oz_per_serving=1.5),
                DrinkType(name="Magic Moments Wine (Budget)", abv_percent=11.0, standard_oz_per_serving=5.0),
                DrinkType(name="Budget Vodka (Generic)", abv_percent=38.0, standard_oz_per_serving=1.5),
                
                # PREMIUM OPTIONS
                DrinkType(name="Jack Daniel's Whiskey", abv_percent=40.0, standard_oz_per_serving=1.5),
                DrinkType(name="Glenmorangie Scotch", abv_percent=43.0, standard_oz_per_serving=1.5),
                DrinkType(name="Blue Label Scotch", abv_percent=40.0, standard_oz_per_serving=1.5),
                
                # International Beer
                DrinkType(name="Budweiser Beer", abv_percent=5.0, standard_oz_per_serving=12.0),
                DrinkType(name="Heineken Beer", abv_percent=5.0, standard_oz_per_serving=12.0),
                DrinkType(name="Corona Beer", abv_percent=4.6, standard_oz_per_serving=12.0),
                
                # Wine
                DrinkType(name="Red Wine", abv_percent=13.5, standard_oz_per_serving=5.0),
                DrinkType(name="White Wine", abv_percent=12.0, standard_oz_per_serving=5.0),
                DrinkType(name="Rose Wine", abv_percent=12.0, standard_oz_per_serving=5.0),
                
                # Liqueurs
                DrinkType(name="Baileys Irish Cream", abv_percent=17.0, standard_oz_per_serving=1.5),
                DrinkType(name="Kahlúa Coffee Liqueur", abv_percent=20.0, standard_oz_per_serving=1.5),
                DrinkType(name="Grand Marnier", abv_percent=40.0, standard_oz_per_serving=1.5),
                
                # Coolers/Refreshers
                DrinkType(name="Smirnoff Ice", abv_percent=4.5, standard_oz_per_serving=12.0),
                DrinkType(name="Breezer", abv_percent=4.8, standard_oz_per_serving=12.0),
                DrinkType(name="UB40 (Malt Beverage)", abv_percent=4.0, standard_oz_per_serving=12.0),
            ]

            db.add_all(default_drinks)
            db.commit()
            print(f"✓ Initialized {len(default_drinks)} drink types (Indian + Global)")
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
