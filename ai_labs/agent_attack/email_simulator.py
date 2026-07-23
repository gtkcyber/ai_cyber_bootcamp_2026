from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import List, Dict, Optional
import uuid
from models import Base, SessionLocal

class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String, unique=True, default=lambda: str(uuid.uuid4()))
    from_address = Column(String, index=True)
    to_address = Column(String, index=True)
    subject = Column(String)
    body = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)
    direction = Column(String)  # "incoming" or "outgoing"
    ai_processed = Column(Boolean, default=False)

class EmailSimulator:
    def __init__(self):
        self.customer_service_email = "support@company.com"

    def create_incoming_email(self, from_address: str, subject: str, body: str) -> Dict:
        """Simulate receiving an email from a customer"""
        db = SessionLocal()
        try:
            email = Email(
                from_address=from_address,
                to_address=self.customer_service_email,
                subject=subject,
                body=body,
                direction="incoming",
                timestamp=datetime.utcnow()
            )
            db.add(email)
            db.commit()
            db.refresh(email)

            return {
                "id": email.id,
                "message_id": email.message_id,
                "from_address": email.from_address,
                "to_address": email.to_address,
                "subject": email.subject,
                "body": email.body,
                "timestamp": email.timestamp,
                "is_read": email.is_read,
                "direction": email.direction,
                "ai_processed": email.ai_processed
            }
        finally:
            db.close()

    def send_response(self, to_address: str, subject: str, body: str, in_reply_to_id: Optional[int] = None) -> Dict:
        """Simulate sending an AI-generated response"""
        db = SessionLocal()
        try:
            # Mark original email as processed if replying
            if in_reply_to_id:
                original_email = db.query(Email).filter(Email.id == in_reply_to_id).first()
                if original_email:
                    original_email.ai_processed = True
                    original_email.is_read = True

            response_email = Email(
                from_address=self.customer_service_email,
                to_address=to_address,
                subject=subject,
                body=body,
                direction="outgoing",
                timestamp=datetime.utcnow(),
                is_read=True  # Outgoing emails are "read" by default
            )
            db.add(response_email)
            db.commit()
            db.refresh(response_email)

            return {
                "id": response_email.id,
                "message_id": response_email.message_id,
                "from_address": response_email.from_address,
                "to_address": response_email.to_address,
                "subject": response_email.subject,
                "body": response_email.body,
                "timestamp": response_email.timestamp,
                "direction": response_email.direction
            }
        finally:
            db.close()

    def get_unread_emails(self) -> List[Dict]:
        """Get all unread incoming emails"""
        db = SessionLocal()
        try:
            emails = db.query(Email).filter(
                Email.direction == "incoming",
                Email.is_read == False
            ).order_by(Email.timestamp.desc()).all()

            return [
                {
                    "id": email.id,
                    "message_id": email.message_id,
                    "from_address": email.from_address,
                    "to_address": email.to_address,
                    "subject": email.subject,
                    "body": email.body,
                    "timestamp": email.timestamp,
                    "is_read": email.is_read,
                    "direction": email.direction,
                    "ai_processed": email.ai_processed
                }
                for email in emails
            ]
        finally:
            db.close()

    def get_all_emails(self, limit: int = 50) -> List[Dict]:
        """Get all emails (both incoming and outgoing)"""
        db = SessionLocal()
        try:
            emails = db.query(Email).order_by(Email.timestamp.desc()).limit(limit).all()

            return [
                {
                    "id": email.id,
                    "message_id": email.message_id,
                    "from_address": email.from_address,
                    "to_address": email.to_address,
                    "subject": email.subject,
                    "body": email.body,
                    "timestamp": email.timestamp,
                    "is_read": email.is_read,
                    "direction": email.direction,
                    "ai_processed": email.ai_processed
                }
                for email in emails
            ]
        finally:
            db.close()

    def mark_as_read(self, email_id: int) -> bool:
        """Mark an email as read"""
        db = SessionLocal()
        try:
            email = db.query(Email).filter(Email.id == email_id).first()
            if email:
                email.is_read = True
                db.commit()
                return True
            return False
        finally:
            db.close()

    def get_conversation_thread(self, customer_email: str) -> List[Dict]:
        """Get all emails in a conversation thread with a customer"""
        db = SessionLocal()
        try:
            emails = db.query(Email).filter(
                (Email.from_address == customer_email) | (Email.to_address == customer_email)
            ).order_by(Email.timestamp.asc()).all()

            return [
                {
                    "id": email.id,
                    "message_id": email.message_id,
                    "from_address": email.from_address,
                    "to_address": email.to_address,
                    "subject": email.subject,
                    "body": email.body,
                    "timestamp": email.timestamp,
                    "direction": email.direction,
                    "ai_processed": email.ai_processed
                }
                for email in emails
            ]
        finally:
            db.close()