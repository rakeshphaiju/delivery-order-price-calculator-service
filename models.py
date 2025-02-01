from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Venue(Base):
    __tablename__ = "venues"

    id = Column(Integer, primary_key=True, index=True)
    venue_slug = Column(String, unique=True, index=True)
    name = Column(String)
    location = Column(JSON)

class DeliverySpecs(Base):
    __tablename__ = "delivery_specs"

    id = Column(Integer, primary_key=True, index=True)
    venue_id = Column(Integer, ForeignKey("venues.id", ondelete="CASCADE"))
    order_minimum_no_surcharge = Column(Integer)
    base_price = Column(Integer)
    distance_ranges = Column(JSON)

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    venue_id = Column(Integer, ForeignKey("venues.id", ondelete="CASCADE"))
    cart_value = Column(Integer)
    user_lat = Column(Float)
    user_lon = Column(Float)
    total_price = Column(Integer)
    small_order_surcharge = Column(Integer)
    delivery_fee = Column(Integer)
    delivery_distance = Column(Integer)
  

