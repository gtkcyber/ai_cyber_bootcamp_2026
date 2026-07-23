from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import logging
from datetime import datetime

from models import get_db, create_tables, Customer, Order, SupportTicket
from email_simulator import EmailSimulator, Email
from ai_agent import AICustomerServiceAgent
from security_monitor import SecurityMonitor
from data_generator import populate_database
from config import settings
from scenarios import scenario_manager
import ollama

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Agent Red Team Testing Platform")

# Mount static files and templates
app.mount("/img", StaticFiles(directory="img"), name="img")
templates = Jinja2Templates(directory="templates")

# Initialize services
email_simulator = EmailSimulator()
ai_agent = AICustomerServiceAgent()
security_monitor = SecurityMonitor()

# Pydantic models for API
class EmailCreate(BaseModel):
    from_address: str
    subject: str
    body: str

class EmailResponse(BaseModel):
    id: int
    message_id: str
    from_address: str
    to_address: str
    subject: str
    body: str
    timestamp: datetime
    direction: str
    is_read: bool
    ai_processed: bool

@app.on_event("startup")
async def startup_event():
    """Initialize database and populate with sample data"""
    logger.info("Starting AI Agent Red Team Testing Platform...")
    create_tables()

    # Check if database is empty and populate if needed
    db = next(get_db())
    customer_count = db.query(Customer).count()
    if customer_count == 0:
        logger.info("Populating database with sample data...")
        populate_database()
    db.close()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Main dashboard showing email inbox and system status"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/emails", response_model=List[EmailResponse])
async def get_emails(limit: int = 50):
    """Get all emails from the simulated inbox"""
    emails = email_simulator.get_all_emails(limit=limit)
    return emails

@app.get("/api/emails/unread", response_model=List[EmailResponse])
async def get_unread_emails():
    """Get only unread emails"""
    emails = email_simulator.get_unread_emails()
    return emails

@app.post("/api/emails", response_model=EmailResponse)
async def create_email(email_data: EmailCreate):
    """Simulate receiving a new email (for red team testing)"""
    try:
        # Create the incoming email
        email = email_simulator.create_incoming_email(
            from_address=email_data.from_address,
            subject=email_data.subject,
            body=email_data.body
        )

        # Log for security monitoring
        security_monitor.log_incoming_email(email)

        logger.info(f"New email received from {email_data.from_address}: {email_data.subject}")
        return email

    except Exception as e:
        logger.error(f"Error creating email: {e}")
        raise HTTPException(status_code=500, detail="Failed to create email")

@app.post("/api/emails/{email_id}/process")
async def process_email(email_id: int, db: Session = Depends(get_db)):
    """Process an email with the AI agent"""
    try:
        # Get the email
        email = db.query(Email).filter(Email.id == email_id).first()
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")

        if email.ai_processed:
            raise HTTPException(status_code=400, detail="Email already processed")

        # Process with AI agent
        response = await ai_agent.process_email(email_id, email.from_address, email.subject, email.body)

        if response:
            # Send the AI response
            response_email = email_simulator.send_response(
                to_address=email.from_address,
                subject=f"Re: {email.subject}",
                body=response["body"],
                in_reply_to_id=email_id
            )

            # Log security events
            security_events = security_monitor.analyze_ai_response(response, email.body)

            return {
                "success": True,
                "response_email": response_email,
                "security_events": security_events
            }
        else:
            raise HTTPException(status_code=500, detail="AI agent failed to process email")

    except Exception as e:
        logger.error(f"Error processing email {email_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process email: {str(e)}")

@app.get("/api/emails/{email_id}")
async def get_email(email_id: int, db: Session = Depends(get_db)):
    """Get a specific email by ID"""
    email = db.query(Email).filter(Email.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    return {
        "id": email.id,
        "message_id": email.message_id,
        "from": email.from_address,
        "to": email.to_address,
        "subject": email.subject,
        "body": email.body,
        "timestamp": email.timestamp,
        "direction": email.direction,
        "is_read": email.is_read,
        "ai_processed": email.ai_processed
    }

@app.post("/api/emails/{email_id}/mark-read")
async def mark_email_read(email_id: int):
    """Mark an email as read"""
    success = email_simulator.mark_as_read(email_id)
    if success:
        return {"success": True}
    else:
        raise HTTPException(status_code=404, detail="Email not found")

@app.get("/api/conversation/{customer_email}")
async def get_conversation(customer_email: str):
    """Get conversation thread with a specific customer"""
    emails = email_simulator.get_conversation_thread(customer_email)
    return emails

@app.get("/api/customers/{customer_email}")
async def get_customer_info(customer_email: str, db: Session = Depends(get_db)):
    """Get customer information from CRM"""
    customer = db.query(Customer).filter(Customer.email == customer_email).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Get recent orders
    orders = db.query(Order).filter(Order.customer_id == customer.id).order_by(Order.order_date.desc()).limit(5).all()

    # Get support tickets
    tickets = db.query(SupportTicket).filter(SupportTicket.customer_id == customer.id).order_by(SupportTicket.created_at.desc()).limit(5).all()

    return {
        "customer": {
            "id": customer.id,
            "email": customer.email,
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "phone": customer.phone,
            "account_balance": customer.account_balance,
            "membership_tier": customer.membership_tier,
            "created_at": customer.created_at,
            "is_active": customer.is_active
        },
        "recent_orders": [
            {
                "id": order.id,
                "order_number": order.order_number,
                "product_name": order.product_name,
                "status": order.status,
                "order_date": order.order_date,
                "price": order.price
            }
            for order in orders
        ],
        "support_tickets": [
            {
                "id": ticket.id,
                "ticket_number": ticket.ticket_number,
                "subject": ticket.subject,
                "status": ticket.status,
                "priority": ticket.priority,
                "created_at": ticket.created_at
            }
            for ticket in tickets
        ]
    }

@app.get("/api/security/events")
async def get_security_events(limit: int = 50):
    """Get recent security events detected by the monitoring system"""
    return security_monitor.get_recent_events(limit)

@app.post("/api/process-all-unread")
async def process_all_unread():
    """Process all unread emails automatically (for demonstration)"""
    try:
        unread_emails = email_simulator.get_unread_emails()
        results = []

        for email in unread_emails:
            try:
                response = await ai_agent.process_email(
                    email["id"],
                    email["from"],
                    email["subject"],
                    email["body"]
                )

                if response:
                    response_email = email_simulator.send_response(
                        to_address=email["from"],
                        subject=f"Re: {email['subject']}",
                        body=response["body"],
                        in_reply_to_id=email["id"]
                    )

                    security_events = security_monitor.analyze_ai_response(response, email["body"])

                    results.append({
                        "email_id": email["id"],
                        "success": True,
                        "response_email": response_email,
                        "security_events": security_events
                    })
                else:
                    results.append({
                        "email_id": email["id"],
                        "success": False,
                        "error": "AI agent failed to generate response"
                    })

            except Exception as e:
                results.append({
                    "email_id": email["id"],
                    "success": False,
                    "error": str(e)
                })

        return {
            "processed_count": len(results),
            "results": results
        }

    except Exception as e:
        logger.error(f"Error processing all unread emails: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process emails: {str(e)}")

@app.post("/api/reset-scenario")
async def reset_scenario(db: Session = Depends(get_db)):
    """Reset the scenario by clearing all emails and security events"""
    try:
        # Count existing records
        email_count = db.query(Email).count()
        events_count = len(security_monitor.get_recent_events())

        # Clear all emails
        db.query(Email).delete()

        # Clear security events from database
        from models import SecurityEvent
        events_deleted = db.query(SecurityEvent).count()
        db.query(SecurityEvent).delete()

        db.commit()

        logger.info(f"Scenario reset: Cleared {email_count} emails and {events_deleted} security events")
        return {
            "message": "Scenario reset successfully",
            "emails_deleted": email_count,
            "events_deleted": events_deleted
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Error resetting scenario: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reset scenario: {str(e)}")

# Configuration API endpoints
class ConfigUpdate(BaseModel):
    ai_provider: str
    ai_model: str
    difficulty_level: str
    enable_guardrails: bool
    enable_content_filtering: bool
    enable_response_validation: bool

@app.post("/api/config")
async def update_config(config: ConfigUpdate):
    """Update AI agent configuration"""
    try:
        # Update settings (in a real application, you'd persist these to a config file or database)
        settings.AI_PROVIDER = config.ai_provider
        settings.AI_MODEL = config.ai_model
        settings.DIFFICULTY_LEVEL = config.difficulty_level
        settings.ENABLE_GUARDRAILS = config.enable_guardrails
        settings.ENABLE_CONTENT_FILTERING = config.enable_content_filtering
        settings.ENABLE_RESPONSE_VALIDATION = config.enable_response_validation

        # Reinitialize AI agent with new settings
        global ai_agent
        ai_agent = AICustomerServiceAgent()

        logger.info(f"Configuration updated: Provider={config.ai_provider}, Model={config.ai_model}, Difficulty={config.difficulty_level}")
        return {"message": "Configuration updated successfully"}

    except Exception as e:
        logger.error(f"Error updating configuration: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update configuration: {str(e)}")

@app.get("/api/config")
async def get_config():
    """Get current AI agent configuration"""
    return {
        "ai_provider": settings.AI_PROVIDER,
        "ai_model": settings.AI_MODEL,
        "difficulty_level": settings.DIFFICULTY_LEVEL,
        "enable_guardrails": settings.ENABLE_GUARDRAILS,
        "enable_content_filtering": settings.ENABLE_CONTENT_FILTERING,
        "enable_response_validation": settings.ENABLE_RESPONSE_VALIDATION
    }

@app.get("/api/ollama/models")
async def get_ollama_models():
    """Get list of available Ollama models"""
    try:
        client = ollama.Client(host=settings.OLLAMA_HOST)
        models = client.list()
        return {"models": models.get('models', [])}
    except Exception as e:
        logger.error(f"Error fetching Ollama models: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch Ollama models: {str(e)}")

# Scenarios API endpoints
@app.get("/api/scenarios")
async def get_scenarios():
    """Get all available attack scenarios"""
    scenarios = scenario_manager.get_all_scenarios()
    return [
        {
            "id": s.id,
            "name": s.name,
            "difficulty": s.difficulty,
            "category": s.category,
            "description": s.description,
            "objective": s.objective,
            "success_criteria": s.success_criteria,
            "sample_email": s.sample_email,
            "hints": s.hints,
            "learning_goals": s.learning_goals,
            "estimated_time": s.estimated_time
        }
        for s in scenarios
    ]

@app.get("/api/scenarios/categories")
async def get_scenario_categories():
    """Get all available scenario categories"""
    return {"categories": scenario_manager.get_scenario_categories()}

@app.get("/api/scenarios/difficulties")
async def get_difficulty_levels():
    """Get all available difficulty levels"""
    return {"difficulties": scenario_manager.get_difficulty_levels()}

@app.get("/api/scenarios/by-difficulty/{difficulty}")
async def get_scenarios_by_difficulty(difficulty: str):
    """Get scenarios filtered by difficulty level"""
    scenarios = scenario_manager.get_scenarios_by_difficulty(difficulty)
    return [
        {
            "id": s.id,
            "name": s.name,
            "difficulty": s.difficulty,
            "category": s.category,
            "description": s.description,
            "estimated_time": s.estimated_time
        }
        for s in scenarios
    ]

@app.get("/api/scenarios/by-category/{category}")
async def get_scenarios_by_category(category: str):
    """Get scenarios filtered by category"""
    scenarios = scenario_manager.get_scenarios_by_category(category)
    return [
        {
            "id": s.id,
            "name": s.name,
            "difficulty": s.difficulty,
            "category": s.category,
            "description": s.description,
            "estimated_time": s.estimated_time
        }
        for s in scenarios
    ]

@app.get("/api/scenarios/{scenario_id}")
async def get_scenario(scenario_id: str):
    """Get a specific scenario by ID"""
    scenario = scenario_manager.get_scenario_by_id(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    return {
        "id": scenario.id,
        "name": scenario.name,
        "difficulty": scenario.difficulty,
        "category": scenario.category,
        "description": scenario.description,
        "objective": scenario.objective,
        "success_criteria": scenario.success_criteria,
        "sample_email": scenario.sample_email,
        "hints": scenario.hints,
        "learning_goals": scenario.learning_goals,
        "estimated_time": scenario.estimated_time
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)