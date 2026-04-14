.PHONY: help install run start stop restart status logs

# Default target
help:
	@echo "Atlas Bot - Makefile Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install     - Install dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make run         - Run bot directly (foreground)"
	@echo "  make test        - Test agent without Discord"
	@echo ""
	@echo "PM2 Process Management:"
	@echo "  make start       - Start bot with PM2"
	@echo "  make stop        - Stop bot"
	@echo "  make restart     - Restart bot"
	@echo "  make status      - Check bot status"
	@echo "  make logs        - View bot logs"
	@echo "  make monitor     - Monitor bot logs in real-time"
	@echo ""
	@echo "Utilities:"
	@echo "  make scrape      - Scrape Bittensor docs"
	@echo "  make collections - List all collections"
	@echo "  make clean       - Clean Python cache files"

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt
	@echo "✅ Installation complete!"
	@echo ""
	@echo "📝 Don't forget to configure your .env file:"
	@echo "   cp .env.example .env"
	@echo "   # Edit .env and add your API keys"

# Run bot directly
run:
	@echo "🚀 Starting Atlas Bot..."
	python run_bot.py

# Test agent
test:
	@echo "🧪 Testing Atlas Agent..."
	python test_agent.py

# Start with PM2
start:
	@echo "🚀 Starting Atlas Bot with PM2..."
	pm2 start ecosystem.config.cjs --name atlas
	@echo "✅ Atlas Bot started!"
	@echo "💬 Use 'make logs' to see logs"
	@echo ""
	@echo "⚠️  Note: Make sure you're in the project directory when starting"

# Stop PM2
stop:
	@echo "🛑 Stopping Atlas Bot..."
	pm2 stop atlas
	@echo "✅ Atlas Bot stopped"

# Restart PM2
restart:
	@echo "🔄 Restarting Atlas Bot..."
	pm2 restart atlas
	@echo "✅ Atlas Bot restarted"

# PM2 Status
status:
	@echo "📊 Atlas Bot Status:"
	@pm2 status atlas

# View logs
logs:
	pm2 logs atlas --lines 50

# Monitor logs in real-time
monitor:
	pm2 logs atlas

# Scrape Bittensor docs
scrape:
	@echo "🕷️  Scraping Bittensor documentation..."
	python main.py scrape https://docs.learnbittensor.org --recursive --max-depth 2 --collection learn_bittensor_understand_bittensor

# List collections
collections:
	@echo "📚 Knowledge Base Collections:"
	python main.py collections

# Clean cache
clean:
	@echo "🧹 Cleaning Python cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@echo "✅ Cache cleaned!"
