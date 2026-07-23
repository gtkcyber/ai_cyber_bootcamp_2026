from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import settings

Base = declarative_base()

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    phone = Column(String)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)
    account_balance = Column(Float, default=0.0)
    membership_tier = Column(String, default="basic")  # basic, premium, vip
    created_at = Column(DateTime, default=datetime.utcnow)
    last_contact = Column(DateTime)
    is_active = Column(Boolean, default=True)
    notes = Column(Text)

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, index=True)
    order_number = Column(String, unique=True)
    product_name = Column(String)
    quantity = Column(Integer)
    price = Column(Float)
    status = Column(String)  # pending, shipped, delivered, cancelled
    order_date = Column(DateTime, default=datetime.utcnow)
    tracking_number = Column(String)

class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, index=True)
    ticket_number = Column(String, unique=True)
    subject = Column(String)
    description = Column(Text)
    status = Column(String, default="open")  # open, in_progress, resolved, closed
    priority = Column(String, default="medium")  # low, medium, high, urgent
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)

class EmailLog(Base):
    __tablename__ = "email_logs"

    id = Column(Integer, primary_key=True, index=True)
    customer_email = Column(String, index=True)
    subject = Column(String)
    body = Column(Text)
    direction = Column(String)  # incoming, outgoing
    timestamp = Column(DateTime, default=datetime.utcnow)
    ai_response = Column(Text)
    security_flags = Column(Text)  # JSON string of security concerns

class SecurityEvent(Base):
    __tablename__ = "security_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String)  # prompt_injection, data_extraction, etc.
    email_id = Column(Integer)
    customer_email = Column(String)
    description = Column(Text)
    severity = Column(String)  # low, medium, high, critical
    detected_at = Column(DateTime, default=datetime.utcnow)
    raw_content = Column(Text)

# Database setup
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()