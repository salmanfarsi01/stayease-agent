from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Date,
    DateTime,
    Text,
    ForeignKey,
    JSON,
    CheckConstraint,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(100), nullable=False)
    address = Column(String(500), nullable=True)
    property_type = Column(String(50), nullable=False)
    price_per_night_bdt = Column(Float, nullable=False)
    max_guests = Column(Integer, nullable=False)
    bedrooms = Column(Integer, nullable=False, default=1)
    amenities = Column(JSON, nullable=True)
    house_rules = Column(Text, nullable=True)
    host_name = Column(String(100), nullable=False)
    host_phone = Column(String(20), nullable=False)
    is_active = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    cover_image_url = Column(String(500), nullable=True)   
    image_urls = Column(JSON, nullable=True)               

    bookings = relationship("Booking", back_populates="listing")

    __table_args__ = (
        CheckConstraint("price_per_night_bdt > 0", name="ck_positive_price"),
        CheckConstraint("max_guests > 0", name="ck_positive_guests"),
    )


class Booking(Base):
    """Confirmed reservations made by guests."""

    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    conversation_id = Column(String(100), nullable=False)    
    guest_name = Column(String(100), nullable=False)
    guest_phone = Column(String(20), nullable=False)
    check_in = Column(Date, nullable=False)
    check_out = Column(Date, nullable=False)
    num_guests = Column(Integer, nullable=False)
    total_cost_bdt = Column(Float, nullable=False)
    status = Column(String(20), nullable=False, default="confirmed") 
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    listing = relationship("Listing", back_populates="bookings")

    __table_args__ = (
        CheckConstraint("check_out > check_in", name="ck_valid_dates"),
        CheckConstraint("num_guests > 0", name="ck_positive_booking_guests"),
    )


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(100), primary_key=True)
    messages = Column(JSON, nullable=False, default=list)
    needs_escalation = Column(Integer, nullable=False, default=0)
    intent = Column(String(50), nullable=True)
    extracted_params = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)