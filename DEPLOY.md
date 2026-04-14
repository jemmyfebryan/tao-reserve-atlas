# VPS Deployment Guide

Deploy Atlas Bot to your VPS with the knowledge base included.

## Prerequisites

On your VPS, install:
```bash
# Python 3.10+
sudo apt update
sudo apt install python3 python3-pip python3-venv -y

# PM2
sudo npm install -g pm2

# Git (if not installed)
sudo apt install git -y
```

## Quick Deploy

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd taoreserve_bot
```

### 2. Setup Environment
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
nano .env  # Add your API keys
```

Required in `.env`:
```env
GEMINI_API_KEY=your_gemini_key
DISCORD_TOKEN=your_discord_token
TARGET_CHANNEL_ID=your_channel_id
```

### 3. Start Bot
```bash
# IMPORTANT: Must be in project directory!
pm2 start ecosystem.config.cjs

# Or use make
make start
```

### 4. Check Status
```bash
pm2 status
pm2 logs atlas
```

## Important Notes

### ⚠️ Working Directory
The `ecosystem.config.cjs` uses relative paths. You **must** run PM2 commands from the project directory:

```bash
# ✅ CORRECT
cd /path/to/taoreserve_bot
pm2 start ecosystem.config.cjs

# ❌ WRONG
pm2 start /path/to/taoreserve_bot/ecosystem.config.cjs
```

### 🔄 Auto-Restart
PM2 will automatically restart the bot if it crashes. To make it persist after server reboot:

```bash
pm2 startup
pm2 save
```

### 📊 Monitoring
```bash
# Check status
pm2 status

# View logs
pm2 logs atlas

# Monitor real-time
pm2 monit

# Restart
pm2 restart atlas

# Stop
pm2 stop atlas
```

## Updating the Bot

When you push changes:

```bash
# Pull latest code
git pull

# Restart bot
pm2 restart atlas

# Or use make
make restart
```

## Database Location

The knowledge base is included in the repo at `data/chroma_db/`. No need to transfer it separately!

## Troubleshooting

**Bot won't start:**
```bash
# Check if in correct directory
pwd  # Should be in taoreserve_bot

# Check logs
pm2 logs atlas --lines 50
```

**Missing dependencies:**
```bash
source .venv/bin/activate
pip install -r requirements.txt
pm2 restart atlas
```

**Wrong interpreter:**
```bash
which python3  # Check path
# Update ecosystem.config.cjs if needed
```

## Makefile Commands

All commands work from project directory:
```bash
make start    # Start with PM2
make stop     # Stop bot
make restart  # Restart bot
make status   # Check status
make logs     # View logs
```
