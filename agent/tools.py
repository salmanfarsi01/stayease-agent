from datetime import date
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from sqlalchemy import and_, not_, exists
from sqlalchemy.orm import Session

from api.database import SessionLocal
from api.models import Listing, Booking


class SearchPropertiesInput(BaseModel):
    location: str = Field(..., description="City or area name, e.g. 'Cox's Bazar'")
    check_in: date = Field(..., description="Check-in date in YYYY-MM-DD format")
    check_out: date = Field(..., description="Check-out date in YYYY-MM-DD format")
    num_guests: int = Field(..., ge=1, description="Number of guests")


class GetListingDetailsInput(BaseModel):
    listing_id: int = Field(..., description="Unique ID of the property listing")


class CreateBookingInput(BaseModel):
    listing_id: int = Field(..., description="ID of the property to book")
    guest_name: str = Field(..., description="Full name of the guest")
    guest_phone: str = Field(..., description="Guest contact phone number")
    check_in: date = Field(..., description="Check-in date in YYYY-MM-DD format")
    check_out: date = Field(..., description="Check-out date in YYYY-MM-DD format")
    num_guests: int = Field(..., ge=1, description="Number of guests")


@tool(args_schema=SearchPropertiesInput)
def search_available_properties(
    location: str,
    check_in: date,
    check_out: date,
    num_guests: int,
) -> dict:
    """Search for available properties matching location, dates, and guest count."""
    db: Session = SessionLocal()
    try:
        # subquery — listings that have a conflicting booking
        conflicting = db.query(Booking.listing_id).filter(
            and_(
                Booking.status == "confirmed",
                Booking.check_in < check_out,
                Booking.check_out > check_in,
            )
        ).subquery()

        # normalize location — strip punctuation for fuzzy matching
        location_clean = location.replace("'", "").replace("'", "").strip()

        listings = db.query(Listing).filter(
            Listing.max_guests >= num_guests,
            Listing.is_active == 1,
            ~Listing.id.in_(conflicting),
        ).all()

        # filter in Python with flexible matching
        listings = [
            l for l in listings
            if location_clean.lower() in l.location.replace("'", "").replace("'", "").lower()
            or l.location.replace("'", "").replace("'", "").lower() in location_clean.lower()
        ]

        return {
    "available": len(listings) > 0,
    "listings": [
        {
            "id": l.id,
            "title": l.title,
            "location": l.location,
            "price_per_night_bdt": l.price_per_night_bdt,
            "max_guests": l.max_guests,
            "type": l.property_type,
            "cover_image_url": l.cover_image_url,
        }
        for l in listings
    ],
    "total_found": len(listings),
}
    finally:
        db.close()


@tool(args_schema=GetListingDetailsInput)
def get_listing_details(listing_id: int) -> dict:
    """Retrieve full details for a specific property listing."""
    db: Session = SessionLocal()
    try:
        listing = db.query(Listing).filter(Listing.id == listing_id).first()
        if not listing:
            return {"error": "Listing not found"}

        return {
        "id": listing.id,
        "title": listing.title,
        "description": listing.description,
        "location": listing.location,
        "address": listing.address,
        "price_per_night_bdt": listing.price_per_night_bdt,
        "max_guests": listing.max_guests,
        "bedrooms": listing.bedrooms,
        "amenities": listing.amenities,
        "house_rules": listing.house_rules,
        "host_name": listing.host_name,
        "host_phone": listing.host_phone,
        "cover_image_url": listing.cover_image_url,   
        "image_urls": listing.image_urls,             
}
    finally:
        db.close()


@tool(args_schema=CreateBookingInput)
def create_booking(
    listing_id: int,
    guest_name: str,
    guest_phone: str,
    check_in: date,
    check_out: date,
    num_guests: int,
) -> dict:
    """Create a confirmed booking for a property."""
    db: Session = SessionLocal()
    try:
        listing = db.query(Listing).filter(Listing.id == listing_id).first()
        if not listing:
            return {"success": False, "booking_id": None, "total_cost_bdt": None, "message": "Listing not found."}

        nights = (check_out - check_in).days
        total = nights * listing.price_per_night_bdt

        booking = Booking(
            listing_id=listing_id,
            conversation_id="",
            guest_name=guest_name,
            guest_phone=guest_phone,
            check_in=check_in,
            check_out=check_out,
            num_guests=num_guests,
            total_cost_bdt=total,
            status="confirmed",
        )
        db.add(booking)
        db.commit()
        db.refresh(booking)

        return {
            "success": True,
            "booking_id": booking.id,
            "total_cost_bdt": total,
            "message": f"Booking confirmed for {guest_name}. {nights} night(s) at BDT {listing.price_per_night_bdt}/night. Total: BDT {total}.",
        }
    finally:
        db.close()


ALL_TOOLS = [search_available_properties, get_listing_details, create_booking]