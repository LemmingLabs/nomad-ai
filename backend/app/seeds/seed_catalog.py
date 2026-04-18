import sys
import logging

from app.core.database import SessionLocal
from app.models.hotel import Hotel
from app.models.place import Place

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_data():
    db = SessionLocal()
    try:
        # Check if data already exists
        hotel_count = db.query(Hotel).count()
        place_count = db.query(Place).count()
        
        if hotel_count > 0 or place_count > 0:
            logger.info("Database already contains catalog data. Skipping seed to prevent duplicates.")
            return

        logger.info("Inserting hotels...")
        hotels = [
            # Bishkek
            Hotel(
                name="Budget Inn Bishkek",
                slug="budget-inn-bishkek",
                city="Bishkek",
                address="Chuy Avenue 120, Bishkek",
                latitude=42.8746,
                longitude=74.5898,
                price_level="low",
                price_from=15,
                rating=4.0,
                description="Affordable and clean accommodation in the heart of Bishkek, perfect for backpackers and budget travelers.",
                amenities=["wifi", "parking", "shared_kitchen"],
                tags=["city", "budget", "backpacking"],
                image_url="/static/hotels/budget-inn-bishkek.jpg"
            ),
            Hotel(
                name="Nomad City Hotel",
                slug="nomad-city-hotel",
                city="Bishkek",
                address="Kievskaya St 77, Bishkek",
                latitude=42.8732,
                longitude=74.5995,
                price_level="medium",
                price_from=45,
                rating=4.5,
                description="Modern comforts meeting traditional Kyrgyz hospitality. Excellent location for exploring the city.",
                amenities=["wifi", "breakfast", "parking", "restaurant", "family_friendly"],
                tags=["city", "family", "comfort"],
                image_url="/static/hotels/nomad-city-hotel.jpg"
            ),
            Hotel(
                name="Bishkek Premium Plaza",
                slug="bishkek-premium-plaza",
                city="Bishkek",
                address="Abdrahmanov St 191, Bishkek",
                latitude=42.8765,
                longitude=74.6110,
                price_level="high",
                price_from=120,
                rating=4.8,
                description="Luxury hotel featuring top-tier spa services, fine dining, and excellent business facilities.",
                amenities=["wifi", "breakfast", "spa", "restaurant", "parking"],
                tags=["city", "luxury", "business", "romantic"],
                image_url="/static/hotels/bishkek-premium-plaza.jpg"
            ),
            
            # Karakol
            Hotel(
                name="Backpacker Hostel Karakol",
                slug="backpacker-hostel-karakol",
                city="Karakol",
                address="Toktogul St 50, Karakol",
                latitude=42.4930,
                longitude=78.3956,
                price_level="low",
                price_from=10,
                rating=4.2,
                description="Cozy atmosphere, great place to meet fellow hikers before heading into the Tian Shan mountains.",
                amenities=["wifi", "parking", "mountain_view"],
                tags=["mountains", "budget", "adventure", "backpacking"],
                image_url="/static/hotels/backpacker-hostel-karakol.jpg"
            ),
            Hotel(
                name="Mountain Lodge Karakol",
                slug="mountain-lodge-karakol",
                city="Karakol",
                address="Karakol Valley Road, Karakol",
                latitude=42.4851,
                longitude=78.4030,
                price_level="medium",
                price_from=40,
                rating=4.6,
                description="Comfortable lodge providing a perfect base camp for skiing and trekking enthusiasts.",
                amenities=["wifi", "breakfast", "parking", "mountain_view", "restaurant"],
                tags=["mountains", "nature", "adventure", "comfort"],
                image_url="/static/hotels/mountain-lodge-karakol.jpg"
            ),
            Hotel(
                name="Karakol Boutique Hotel",
                slug="karakol-boutique-hotel",
                city="Karakol",
                address="Gagarin St 15, Karakol",
                latitude=42.4900,
                longitude=78.3900,
                price_level="high",
                price_from=90,
                rating=4.9,
                description="Premium hotel offering warm rooms, superior services after a cold day in the mountains, and excellent local dining.",
                amenities=["wifi", "breakfast", "spa", "restaurant", "mountain_view"],
                tags=["mountains", "luxury", "romantic", "comfort"],
                image_url="/static/hotels/karakol-boutique-hotel.jpg"
            ),
            
            # Cholpon-Ata
            Hotel(
                name="Lakeside Guesthouse",
                slug="lakeside-guesthouse",
                city="Cholpon-Ata",
                address="Sovetskaya St 10, Cholpon-Ata",
                latitude=42.6480,
                longitude=77.0860,
                price_level="low",
                price_from=20,
                rating=4.1,
                description="Simple and welcoming guesthouse just a short walk from Issyk-Kul lake.",
                amenities=["wifi", "parking", "family_friendly"],
                tags=["lake", "budget", "family"],
                image_url="/static/hotels/lakeside-guesthouse.jpg"
            ),
            Hotel(
                name="Beach Resort Cholpon-Ata",
                slug="beach-resort-cholpon-ata",
                city="Cholpon-Ata",
                address="Lake Shore Blvd 5, Cholpon-Ata",
                latitude=42.6455,
                longitude=77.0890,
                price_level="medium",
                price_from=60,
                rating=4.5,
                description="Modern resort offering private beach access, ideal for family vacations and summer getaways.",
                amenities=["wifi", "breakfast", "parking", "lake_view", "family_friendly", "restaurant"],
                tags=["lake", "family", "comfort", "nature"],
                image_url="/static/hotels/beach-resort-cholpon-ata.jpg"
            ),
            Hotel(
                name="Issyk-Kul Premium Resort",
                slug="issyk-kul-premium-resort",
                city="Cholpon-Ata",
                address="Gold Sand Avenue 1, Cholpon-Ata",
                latitude=42.6400,
                longitude=77.0950,
                price_level="high",
                price_from=150,
                rating=4.8,
                description="Five-star luxury by the lake, featuring private beaches, spa centers, and exquisite dining options.",
                amenities=["wifi", "breakfast", "parking", "lake_view", "spa", "restaurant", "family_friendly"],
                tags=["lake", "luxury", "romantic", "family"],
                image_url="/static/hotels/issyk-kul-premium-resort.jpg"
            ),
        ]
        
        db.add_all(hotels)

        logger.info("Inserting places...")
        places = [
            # Bishkek
            Place(
                name="Faiza",
                slug="faiza-bishkek",
                type="cafe",
                city="Bishkek",
                address="Jibek Jolu 555, Bishkek",
                latitude=42.8850,
                longitude=74.5800,
                price_level="low",
                average_check=5,
                rating=4.6,
                description="Legendary local cafe famous for lagman and manty. Fast service and very authentic.",
                tags=["food", "local", "budget"],
                image_url="/static/places/faiza.jpg"
            ),
            Place(
                name="Navat",
                slug="navat-bishkek",
                type="restaurant",
                city="Bishkek",
                address="Togolok Moldo 114, Bishkek",
                latitude=42.8750,
                longitude=74.5950,
                price_level="medium",
                average_check=15,
                rating=4.7,
                description="Traditional Kyrgyz restaurant with colorful national interior and great hospitality.",
                tags=["food", "local", "culture", "family"],
                image_url="/static/places/navat.jpg"
            ),
            Place(
                name="Ala-Too Square",
                slug="ala-too-square",
                type="attraction",
                city="Bishkek",
                address="Chuy Avenue, Bishkek",
                latitude=42.8764,
                longitude=74.6038,
                price_level="free",
                average_check=0,
                rating=4.5,
                description="The central square of Bishkek, featuring the Manas monument and the changing of the guards.",
                tags=["city", "culture"],
                image_url="/static/places/ala-too-square.jpg"
            ),
            Place(
                name="Osh Bazaar",
                slug="osh-bazaar",
                type="attraction",
                city="Bishkek",
                address="Chuy Avenue 255, Bishkek",
                latitude=42.8780,
                longitude=74.5700,
                price_level="free",
                average_check=0,
                rating=4.3,
                description="One of the largest bazaars in Bishkek, great for buying local snacks, spices, and souvenirs.",
                tags=["city", "local", "culture"],
                image_url="/static/places/osh-bazaar.jpg"
            ),
            Place(
                name="State Historical Museum",
                slug="state-historical-museum",
                type="activity",
                city="Bishkek",
                address="Ala-Too Square, Bishkek",
                latitude=42.8770,
                longitude=74.6040,
                price_level="low",
                average_check=3,
                rating=4.6,
                description="Extensive collection of Kyrgyz cultural and historical artifacts.",
                tags=["city", "culture", "family"],
                image_url="/static/places/historical-museum.jpg"
            ),
            Place(
                name="Supara Ethno-Complex",
                slug="supara-ethno-complex",
                type="restaurant",
                city="Bishkek",
                address="Karagul Akmat 1a, Bishkek",
                latitude=42.8050,
                longitude=74.6150,
                price_level="high",
                average_check=35,
                rating=4.8,
                description="A unique ethno-complex offering high-end traditional cuisine in stylized yurts and stone houses.",
                tags=["food", "local", "culture", "romantic", "luxury"],
                image_url="/static/places/supara.jpg"
            ),
            
            # Karakol
            Place(
                name="Karakol Coffee",
                slug="karakol-coffee",
                type="cafe",
                city="Karakol",
                address="Toktogul 110, Karakol",
                latitude=42.4920,
                longitude=78.3960,
                price_level="low",
                average_check=4,
                rating=4.5,
                description="Cozy coffee shop popular among backpackers, serving excellent coffee and breakfast.",
                tags=["food", "city"],
                image_url="/static/places/karakol-coffee.jpg"
            ),
            Place(
                name="Dastorkon",
                slug="dastorkon-karakol",
                type="restaurant",
                city="Karakol",
                address="Przhevalsky St, Karakol",
                latitude=42.4935,
                longitude=78.3970,
                price_level="medium",
                average_check=12,
                rating=4.7,
                description="Top-rated traditional restaurant in Karakol, famous for Ashlan-Fu and lagman.",
                tags=["food", "local", "culture", "family"],
                image_url="/static/places/dastorkon.jpg"
            ),
            Place(
                name="Dungan Mosque",
                slug="dungan-mosque",
                type="attraction",
                city="Karakol",
                address="Bektenov St, Karakol",
                latitude=42.4950,
                longitude=78.3940,
                price_level="free",
                average_check=0,
                rating=4.6,
                description="Unique wooden mosque built in Chinese architectural style without a single nail.",
                tags=["city", "culture"],
                image_url="/static/places/dungan-mosque.jpg"
            ),
            Place(
                name="Holy Trinity Cathedral",
                slug="holy-trinity-cathedral",
                type="attraction",
                city="Karakol",
                address="Lenin St, Karakol",
                latitude=42.4900,
                longitude=78.3920,
                price_level="free",
                average_check=0,
                rating=4.5,
                description="Historic Russian Orthodox church built entirely of wood, surrounded by a peaceful garden.",
                tags=["city", "culture"],
                image_url="/static/places/holy-trinity.jpg"
            ),
            Place(
                name="Karakol Ski Resort",
                slug="karakol-ski-resort",
                type="activity",
                city="Karakol",
                address="Karakol Gorge",
                latitude=42.4400,
                longitude=78.4700,
                price_level="high",
                average_check=25,
                rating=4.8,
                description="Famous ski base with excellent slopes and deep powder snow, surrounded by pine forests.",
                tags=["mountains", "adventure", "nature"],
                image_url="/static/places/karakol-ski.jpg"
            ),
            Place(
                name="Karakol Valley Hiking Trail",
                slug="karakol-valley-hiking",
                type="activity",
                city="Karakol",
                address="Karakol National Park",
                latitude=42.4100,
                longitude=78.4800,
                price_level="free",
                average_check=0,
                rating=4.9,
                description="Stunning hiking trails leading to alpine lakes and hot springs in the Tian Shan mountains.",
                tags=["mountains", "nature", "adventure"],
                image_url="/static/places/karakol-hiking.jpg"
            ),
            
            # Cholpon-Ata
            Place(
                name="Lake View Cafe",
                slug="lake-view-cafe",
                type="cafe",
                city="Cholpon-Ata",
                address="Beach Blvd, Cholpon-Ata",
                latitude=42.6460,
                longitude=77.0870,
                price_level="low",
                average_check=6,
                rating=4.2,
                description="Casual lakeside cafe offering snacks, fresh drinks, and a beautiful view of Issyk-Kul.",
                tags=["food", "lake", "nature"],
                image_url="/static/places/lake-view-cafe.jpg"
            ),
            Place(
                name="U Rybaka",
                slug="u-rybaka-cholpon-ata",
                type="restaurant",
                city="Cholpon-Ata",
                address="Sovetskaya 2, Cholpon-Ata",
                latitude=42.6485,
                longitude=77.0850,
                price_level="medium",
                average_check=14,
                rating=4.5,
                description="Famous restaurant specializing in freshly caught fish from the lake.",
                tags=["food", "local", "lake", "family"],
                image_url="/static/places/u-rybaka.jpg"
            ),
            Place(
                name="Rukh Ordo Cultural Center",
                slug="rukh-ordo",
                type="attraction",
                city="Cholpon-Ata",
                address="Sovetskaya St, Cholpon-Ata",
                latitude=42.6490,
                longitude=77.0800,
                price_level="medium",
                average_check=8,
                rating=4.7,
                description="A beautiful spiritual and cultural complex celebrating different religions and Kyrgyz heritage.",
                tags=["culture", "lake", "family"],
                image_url="/static/places/rukh-ordo.jpg"
            ),
            Place(
                name="Petroglyphs Open Air Museum",
                slug="petroglyphs-museum",
                type="attraction",
                city="Cholpon-Ata",
                address="Northern Outskirts, Cholpon-Ata",
                latitude=42.6600,
                longitude=77.0700,
                price_level="low",
                average_check=2,
                rating=4.4,
                description="An open-air museum featuring thousands of ancient rock carvings dating back thousands of years.",
                tags=["culture", "nature"],
                image_url="/static/places/petroglyphs.jpg"
            ),
            Place(
                name="Boat Cruise Issyk-Kul",
                slug="boat-cruise-issyk-kul",
                type="activity",
                city="Cholpon-Ata",
                address="Main Pier, Cholpon-Ata",
                latitude=42.6420,
                longitude=77.0880,
                price_level="medium",
                average_check=10,
                rating=4.6,
                description="Relaxing boat tours on the crystal clear waters of Issyk-Kul lake.",
                tags=["lake", "nature", "family", "romantic"],
                image_url="/static/places/boat-cruise.jpg"
            ),
            Place(
                name="Cholpon-Ata Beach",
                slug="cholpon-ata-beach",
                type="activity",
                city="Cholpon-Ata",
                address="Central Beach, Cholpon-Ata",
                latitude=42.6450,
                longitude=77.0890,
                price_level="free",
                average_check=0,
                rating=4.5,
                description="The main public sandy beach, perfect for swimming and sunbathing during summer.",
                tags=["lake", "nature", "family"],
                image_url="/static/places/cholpon-ata-beach.jpg"
            ),
        ]
        
        db.add_all(places)
        db.commit()
        logger.info("Successfully seeded 9 hotels and 18 places!")
        
    except Exception as e:
        logger.error(f"Error seeding data: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("Starting catalog seed script...")
    seed_data()
