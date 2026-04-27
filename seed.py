import os
import sys
from dotenv import load_dotenv

# add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from api.database import init_db, SessionLocal
from api.models import Listing
listings_data = [
    {
        "title": "Sea View Suite",
        "description": "Modern beachfront apartment with full sea view and private balcony.",
        "location": "Cox's Bazar",
        "address": "Kolatoli Road, Cox's Bazar",
        "property_type": "apartment",
        "price_per_night_bdt": 4500.0,
        "max_guests": 4,
        "bedrooms": 2,
        "amenities": ["WiFi", "AC", "Hot water", "Parking", "Sea view"],
        "house_rules": "No smoking. Check-in after 2 PM. Check-out before 11 AM.",
        "host_name": "Rahim Uddin",
        "host_phone": "+8801711000001",
        "is_active": 1,
        "cover_image_url": "https://images.unsplash.com/photo-1566073771259-6a8506099945",
        "image_urls": [
            "https://images.unsplash.com/photo-1566073771259-6a8506099945",
            "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4",
        ],
    },
    {
        "title": "Ocean Breeze Cottage",
        "description": "Cozy cottage 5 minutes walk from the beach, great for families.",
        "location": "Cox's Bazar",
        "address": "Sugandha Beach Road, Cox's Bazar",
        "property_type": "house",
        "price_per_night_bdt": 3200.0,
        "max_guests": 3,
        "bedrooms": 1,
        "amenities": ["WiFi", "AC", "Kitchen", "Hot water"],
        "house_rules": "No parties. Quiet hours after 10 PM.",
        "host_name": "Karim Hossain",
        "host_phone": "+8801711000002",
        "is_active": 1,
        "cover_image_url": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4",
        "image_urls": [
            "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4",
        ],
    },
    {
        "title": "Sylhet Tea Garden Villa",
        "description": "Luxury villa surrounded by tea gardens with stunning hill views.",
        "location": "Sylhet",
        "address": "Jaflong Road, Sylhet",
        "property_type": "house",
        "price_per_night_bdt": 6000.0,
        "max_guests": 6,
        "bedrooms": 3,
        "amenities": ["WiFi", "AC", "Garden", "Parking", "Hot water", "BBQ"],
        "house_rules": "No smoking indoors. Pets allowed.",
        "host_name": "Nusrat Jahan",
        "host_phone": "+8801811000001",
        "is_active": 1,
        "cover_image_url": "https://images.unsplash.com/photo-1587974928442-77dc3e0dba72",
        "image_urls": [
            "https://images.unsplash.com/photo-1587974928442-77dc3e0dba72",
        ],
    },
    {
        "title": "Dhaka City Center Apartment",
        "description": "Modern studio apartment in Gulshan, close to restaurants and offices.",
        "location": "Dhaka",
        "address": "Gulshan-2, Dhaka",
        "property_type": "apartment",
        "price_per_night_bdt": 2800.0,
        "max_guests": 2,
        "bedrooms": 1,
        "amenities": ["WiFi", "AC", "Security", "Elevator", "Hot water"],
        "house_rules": "No smoking. No extra guests.",
        "host_name": "Farhan Ahmed",
        "host_phone": "+8801911000001",
        "is_active": 1,
        "cover_image_url": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267",
        "image_urls": [
            "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267",
        ],
    },
    {
        "title": "Banani Executive Suite",
        "description": "Spacious executive suite in Banani with full kitchen and workspace.",
        "location": "Dhaka",
        "address": "Banani Block D, Dhaka",
        "property_type": "apartment",
        "price_per_night_bdt": 3500.0,
        "max_guests": 3,
        "bedrooms": 2,
        "amenities": ["WiFi", "AC", "Kitchen", "Workspace", "Hot water", "Parking"],
        "house_rules": "Check-in after 3 PM. No loud music after 11 PM.",
        "host_name": "Sultana Begum",
        "host_phone": "+8801911000002",
        "is_active": 1,
        "cover_image_url": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267",
        "image_urls": [
            "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267",
        ],
    },
    {
        "title": "Sundarbans Edge Resort Room",
        "description": "Eco-friendly room at the edge of Sundarbans, perfect for nature lovers.",
        "location": "Khulna",
        "address": "Mongla Port Road, Khulna",
        "property_type": "room",
        "price_per_night_bdt": 1800.0,
        "max_guests": 2,
        "bedrooms": 1,
        "amenities": ["WiFi", "Fan", "Mosquito net", "Breakfast included"],
        "house_rules": "No plastic. Eco-friendly stay. Lights out by 11 PM.",
        "host_name": "Mizanur Rahman",
        "host_phone": "+8801611000001",
        "is_active": 1,
        "cover_image_url": "https://images.unsplash.com/photo-1596436889106-be35e843f974",
        "image_urls": [
            "https://images.unsplash.com/photo-1596436889106-be35e843f974",
        ],
    },
    {
        "title": "Rangamati Lake House",
        "description": "Beautiful house on the banks of Kaptai Lake with boat access.",
        "location": "Rangamati",
        "address": "Kaptai Lake Shore, Rangamati",
        "property_type": "house",
        "price_per_night_bdt": 5000.0,
        "max_guests": 5,
        "bedrooms": 2,
        "amenities": ["WiFi", "AC", "Lake view", "Boat", "Hot water", "Kitchen"],
        "house_rules": "Life jackets mandatory for lake activities. No alcohol.",
        "host_name": "Chakma Raju",
        "host_phone": "+8801511000001",
        "is_active": 1,
        "cover_image_url": "https://images.unsplash.com/photo-1499793983690-e29da59ef1c2",
        "image_urls": [
            "https://images.unsplash.com/photo-1499793983690-e29da59ef1c2",
        ],
    },
    {
        "title": "Saint Martin Beach Hut",
        "description": "Simple but charming beach hut right on Saint Martin Island shore.",
        "location": "Saint Martin",
        "address": "North Beach, Saint Martin Island",
        "property_type": "room",
        "price_per_night_bdt": 2200.0,
        "max_guests": 2,
        "bedrooms": 1,
        "amenities": ["Fan", "Beach access", "Breakfast included", "Snorkeling gear"],
        "house_rules": "No smoking on beach. Check-out by 10 AM.",
        "host_name": "Jamal Sikder",
        "host_phone": "+8801711000003",
        "is_active": 1,
        "cover_image_url": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4",
        "image_urls": [
            "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4",
        ],
    },
]


def seed():
    init_db()
    db = SessionLocal()

    existing = db.query(Listing).count()
    if existing > 0:
        print(f"Database already has {existing} listings. Skipping seed.")
        db.close()
        return

    for data in listings_data:
        listing = Listing(**data)
        db.add(listing)

    db.commit()
    db.close()
    print(f"Seeded {len(listings_data)} listings successfully.")


if __name__ == "__main__":
    seed()