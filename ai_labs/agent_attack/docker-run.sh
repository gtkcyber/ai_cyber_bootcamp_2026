#!/bin/bash

# AI Agent Red Team Testing Platform - Docker Runner
# This script helps you run the application with different configurations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 AI Agent Red Team Testing Platform${NC}"
echo -e "${BLUE}=====================================${NC}"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  No .env file found. Creating template...${NC}"
    cat > .env << EOF
# AI Provider Configuration
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Application Settings
AI_PROVIDER=openai
AI_MODEL=gpt-3.5-turbo
DIFFICULTY_LEVEL=medium
EOF
    echo -e "${GREEN}✅ Created .env template. Please edit it with your API keys.${NC}"
fi

# Create data directory if it doesn't exist
mkdir -p data

# Function to show usage
show_usage() {
    echo -e "${YELLOW}Usage:${NC}"
    echo "  $0 [option]"
    echo ""
    echo -e "${YELLOW}Options:${NC}"
    echo "  start         - Start the application (default)"
    echo "  start-ollama  - Start with local Ollama support"
    echo "  build         - Build the Docker image"
    echo "  logs          - Show application logs"
    echo "  stop          - Stop the application"
    echo "  clean         - Stop and remove containers/volumes"
    echo "  help          - Show this help message"
}

# Parse command line arguments
case "${1:-start}" in
    "start")
        echo -e "${GREEN}🔧 Starting AI Agent Red Team Platform...${NC}"
        docker-compose up -d ai-agent-redteam
        echo -e "${GREEN}✅ Application started at http://localhost:8000${NC}"
        echo -e "${BLUE}📝 Check logs with: $0 logs${NC}"
        ;;

    "start-ollama")
        echo -e "${GREEN}🔧 Starting with Ollama support...${NC}"
        docker-compose --profile ollama up -d
        echo -e "${GREEN}✅ Application with Ollama started at http://localhost:8000${NC}"
        echo -e "${BLUE}📝 Ollama available at http://localhost:11434${NC}"
        echo -e "${BLUE}📝 Check logs with: $0 logs${NC}"
        ;;

    "build")
        echo -e "${GREEN}🔨 Building Docker image...${NC}"
        docker-compose build
        echo -e "${GREEN}✅ Build complete${NC}"
        ;;

    "logs")
        echo -e "${BLUE}📝 Showing application logs...${NC}"
        docker-compose logs -f ai-agent-redteam
        ;;

    "stop")
        echo -e "${YELLOW}🛑 Stopping application...${NC}"
        docker-compose down
        echo -e "${GREEN}✅ Application stopped${NC}"
        ;;

    "clean")
        echo -e "${RED}🧹 Cleaning up containers and volumes...${NC}"
        read -p "This will remove all containers and volumes. Continue? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose down -v
            docker-compose --profile ollama down -v
            echo -e "${GREEN}✅ Cleanup complete${NC}"
        else
            echo -e "${BLUE}❌ Cleanup cancelled${NC}"
        fi
        ;;

    "help"|"-h"|"--help")
        show_usage
        ;;

    *)
        echo -e "${RED}❌ Unknown option: $1${NC}"
        show_usage
        exit 1
        ;;
esac