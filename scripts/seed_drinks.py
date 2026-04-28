"""
Seed DrinkType database with comprehensive global and Indian drinks.
Integrates TheCocktailDB API with curated Indian spirits and regional drinks.

Run from project root: python scripts/seed_drinks.py
"""

import requests
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal, engine
from app.models import Base, DrinkType

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)


def fetch_cocktaildb_drinks():
    """Fetch popular drinks from TheCocktailDB API (free, no auth required)."""
    drinks = []
    base_url = "https://www.thecocktaildb.com/api/json/v1/1"
    
    # Get drinks by first letter (A-Z)
    for letter in "abcdefghijklmnopqrstuvwxyz":
        try:
            response = requests.get(f"{base_url}/search.php?f={letter}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("drinks"):
                    for drink in data["drinks"]:
                        # Extract ingredients and ABV if available
                        name = drink.get("strDrink", "Unknown")
                        # CocktailDB doesn't have standard ABV in list API, so we estimate by type
                        abv = estimate_abv_from_cocktail(drink)
                        drinks.append({
                            "name": name,
                            "abv_percent": abv,
                            "standard_oz_per_serving": 5.0,  # Standard cocktail ~5 oz
                            "source": "CocktailDB"
                        })
        except Exception as e:
            print(f"Error fetching drinks for letter {letter}: {e}")
    
    return drinks


def estimate_abv_from_cocktail(cocktail_data):
    """Estimate ABV based on cocktail type/name."""
    name = cocktail_data.get("strDrink", "").lower()
    
    # Estimate ABV based on cocktail type
    if any(x in name for x in ["shot", "shooter"]):
        return 40.0
    elif any(x in name for x in ["beer", "ale", "lager"]):
        return 5.0
    elif any(x in name for x in ["wine", "sangria"]):
        return 12.0
    elif any(x in name for x in ["vodka"]):
        return 40.0
    elif any(x in name for x in ["rum"]):
        return 40.0
    elif any(x in name for x in ["whiskey", "whisky", "bourbon"]):
        return 40.0
    elif any(x in name for x in ["gin"]):
        return 40.0
    elif any(x in name for x in ["tequila"]):
        return 40.0
    elif any(x in name for x in ["punch", "cocktail"]):
        return 15.0
    else:
        return 20.0  # Default estimate for mixed drinks


# Comprehensive list of Indian and Regional Drinks with accurate ABV
INDIAN_DRINKS = [
    # Popular Indian Spirits
    {"name": "Old Monk Rum", "abv_percent": 42.8, "standard_oz_per_serving": 1.5},
    {"name": "Royal Challenge Whiskey", "abv_percent": 42.8, "standard_oz_per_serving": 1.5},
    {"name": "Johnnie Walker Red Label", "abv_percent": 40.0, "standard_oz_per_serving": 1.5},
    {"name": "McDowell's No. 1 Whiskey", "abv_percent": 42.8, "standard_oz_per_serving": 1.5},
    {"name": "Bacardi Rum", "abv_percent": 37.5, "standard_oz_per_serving": 1.5},
    {"name": "Kingfisher Beer", "abv_percent": 4.2, "standard_oz_per_serving": 12.0},
    {"name": "Tuborg Beer", "abv_percent": 4.8, "standard_oz_per_serving": 12.0},
    {"name": "Carlsberg Beer", "abv_percent": 4.6, "standard_oz_per_serving": 12.0},
    {"name": "Cobra Beer", "abv_percent": 4.0, "standard_oz_per_serving": 12.0},
    {"name": "Thunderbolt Beer", "abv_percent": 7.2, "standard_oz_per_serving": 12.0},
    
    # Regional Spirits
    {"name": "Feni (Cashew Liquor)", "abv_percent": 42.0, "standard_oz_per_serving": 1.5},
    {"name": "Arrack (Coconut/Palm)", "abv_percent": 45.0, "standard_oz_per_serving": 1.5},
    {"name": "Toddy/Tadi (Palm Wine)", "abv_percent": 6.0, "standard_oz_per_serving": 5.0},
    {"name": "Mahua (Flower Wine)", "abv_percent": 16.0, "standard_oz_per_serving": 5.0},
    {"name": "Raksi (Rice Wine)", "abv_percent": 18.0, "standard_oz_per_serving": 5.0},
    {"name": "Chhang (Barley Wine)", "abv_percent": 6.0, "standard_oz_per_serving": 5.0},
    
    # Tamil Nadu Drinks (TASMAC)
    {"name": "Samrakshan (TASMAC Brand)", "abv_percent": 42.8, "standard_oz_per_serving": 1.5},
    {"name": "Kanya Brandy", "abv_percent": 42.8, "standard_oz_per_serving": 1.5},
    {"name": "Charminar Brandy", "abv_percent": 42.8, "standard_oz_per_serving": 1.5},
    
    # Indian Wine
    {"name": "Sula Wines (Red)", "abv_percent": 13.0, "standard_oz_per_serving": 5.0},
    {"name": "Grover Zampa Cabernet Sauvignon", "abv_percent": 13.5, "standard_oz_per_serving": 5.0},
    {"name": "Reveilo Wines (White)", "abv_percent": 12.0, "standard_oz_per_serving": 5.0},
    
    # Prepared Mixed Drinks
    {"name": "Kingfisher Strong (Premium Beer)", "abv_percent": 6.8, "standard_oz_per_serving": 12.0},
    {"name": "Godfather (Whiskey+Brandy)", "abv_percent": 40.0, "standard_oz_per_serving": 1.5},
    
    # International Spirits (Popular in India)
    {"name": "Smirnoff Vodka", "abv_percent": 40.0, "standard_oz_per_serving": 1.5},
    {"name": "Jägermeister", "abv_percent": 35.0, "standard_oz_per_serving": 1.5},
    {"name": "Budweiser Beer", "abv_percent": 5.0, "standard_oz_per_serving": 12.0},
    {"name": "Heineken Beer", "abv_percent": 5.0, "standard_oz_per_serving": 12.0},
    {"name": "Corona Beer", "abv_percent": 4.6, "standard_oz_per_serving": 12.0},
    
    # Wines
    {"name": "Red Wine (Generic)", "abv_percent": 13.5, "standard_oz_per_serving": 5.0},
    {"name": "White Wine (Generic)", "abv_percent": 12.0, "standard_oz_per_serving": 5.0},
    {"name": "Rose Wine", "abv_percent": 12.0, "standard_oz_per_serving": 5.0},
    
    # Liqueurs
    {"name": "Baileys Irish Cream", "abv_percent": 17.0, "standard_oz_per_serving": 1.5},
    {"name": "Kahlúa Coffee Liqueur", "abv_percent": 20.0, "standard_oz_per_serving": 1.5},
    {"name": "Grand Marnier", "abv_percent": 40.0, "standard_oz_per_serving": 1.5},
    
    # Refreshers/Coolers (Low Alcohol)
    {"name": "Smirnoff Ice", "abv_percent": 4.5, "standard_oz_per_serving": 12.0},
    {"name": "Breezer", "abv_percent": 4.8, "standard_oz_per_serving": 12.0},
    {"name": "UB40 (Malt Beverage)", "abv_percent": 4.0, "standard_oz_per_serving": 12.0},
]


def add_drinks_to_db(drinks_list):
    """Add drinks to database, avoiding duplicates."""
    db = SessionLocal()
    added_count = 0
    skipped_count = 0
    
    try:
        for drink_data in drinks_list:
            # Check if drink already exists
            existing = db.query(DrinkType).filter(
                DrinkType.name == drink_data["name"]
            ).first()
            
            if existing:
                skipped_count += 1
                continue
            
            # Create new drink
            drink = DrinkType(
                name=drink_data["name"],
                abv_percent=drink_data["abv_percent"],
                standard_oz_per_serving=drink_data["standard_oz_per_serving"]
            )
            db.add(drink)
            added_count += 1
        
        db.commit()
        print(f"✅ Added {added_count} new drinks")
        print(f"⏭️  Skipped {skipped_count} existing drinks")
        
    except Exception as e:
        print(f"❌ Error adding drinks: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """Main seeding function."""
    print("🍺 DrinkType Database Seeder")
    print("=" * 50)
    
    # Start with Indian drinks (guaranteed accurate)
    print("📍 Adding Indian & Regional Drinks...")
    add_drinks_to_db(INDIAN_DRINKS)
    
    # Try to fetch international cocktails from CocktailDB
    print("\n🌍 Fetching International Cocktails from TheCocktailDB...")
    try:
        cocktail_drinks = fetch_cocktaildb_drinks()
        if cocktail_drinks:
            print(f"📥 Retrieved {len(cocktail_drinks)} cocktails from TheCocktailDB")
            add_drinks_to_db(cocktail_drinks)
        else:
            print("⚠️  No cocktails fetched (API may be unavailable)")
    except Exception as e:
        print(f"⚠️  Could not fetch from TheCocktailDB: {e}")
        print("💡 This is okay - Indian drinks are already seeded!")
    
    print("\n" + "=" * 50)
    
    # Show total drinks in DB
    db = SessionLocal()
    total = db.query(DrinkType).count()
    db.close()
    print(f"✅ Total drinks in database: {total}")


if __name__ == "__main__":
    main()
