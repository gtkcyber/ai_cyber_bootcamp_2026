#!/usr/bin/env python3
"""
AI Agent Red Team Testing Platform
Run this script to start the application
"""

import uvicorn
import logging
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.append(str(Path(__file__).parent))

from config import settings
from models import create_tables
from data_generator import populate_database

def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('app.log')
        ]
    )

def initialize_database():
    """Initialize database and populate with sample data if empty"""
    print("Initializing database...")
    create_tables()

    # Check if we need to populate sample data
    from models import SessionLocal, Customer
    db = SessionLocal()
    try:
        customer_count = db.query(Customer).count()
        if customer_count == 0:
            print("Database is empty. Populating with sample data...")
            populate_database()
            print("Sample data created successfully!")
        else:
            print(f"Database already contains {customer_count} customers.")
    finally:
        db.close()

def main():
    """Main entry point for the application"""
    print("🔴 AI Agent Red Team Testing Platform")
    print("=" * 50)

    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)

    # Initialize database
    try:
        initialize_database()
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        print(f"❌ Database initialization failed: {e}")
        return 1

    # Check AI provider configuration
    if settings.AI_PROVIDER == "openai" and not settings.OPENAI_API_KEY:
        print("⚠️  OpenAI API key not configured. The AI agent will use mock responses.")
        print("   Set OPENAI_API_KEY in .env file for real AI responses.")
    elif settings.AI_PROVIDER == "anthropic" and not settings.ANTHROPIC_API_KEY:
        print("⚠️  Anthropic API key not configured. The AI agent will use mock responses.")
        print("   Set ANTHROPIC_API_KEY in .env file for real AI responses.")
    else:
        print(f"✅ AI Provider configured: {settings.AI_PROVIDER} ({settings.AI_MODEL})")

    print("\n🚀 Starting web server...")
    print("   📊 Dashboard: http://localhost:8000")
    print("   📚 API Docs: http://localhost:8000/docs")
    print("\n🔧 Red Team Testing Features:")
    print("   • Craft malicious emails in the web interface")
    print("   • Monitor AI agent responses in real-time")
    print("   • Track security events and vulnerabilities")
    print("   • Analyze prompt injection attempts")
    print("   • Test data extraction attacks")
    print("\n⚠️  This is a SECURITY TESTING tool. Use only in authorized environments.")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 50)

    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=settings.DEBUG,
            log_level=settings.LOG_LEVEL.lower()
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        print(f"❌ Failed to start server: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())