# Atlas Bot Setup Guide

Quick setup guide to get Atlas running on your Discord server.

## Prerequisites

- Python 3.10+
- Discord account
- Google account (for Gemini API)

## Step 1: Install Dependencies

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Step 2: Get API Keys

### Gemini API Key
1. Go to https://makersuite.google.com/app/apikey
2. Create a new API key
3. Copy it

### Discord Bot Token
1. Go to https://discord.com/developers/applications
2. Click "New Application" → Name it "Atlas"
3. Go to "Bot" → "Add Bot"
4. Copy the token
5. **Important**: Enable "Message Content Intent"

### Get Channel ID
1. Enable Developer Mode in Discord (Settings → Advanced)
2. Right-click your target channel
3. Copy ID

## Step 3: Configure Environment

Create `.env` file:
```bash
cp .env.example .env
```

Edit `.env`:
```env
GEMINI_API_KEY=your_actual_gemini_key
DISCORD_TOKEN=your_actual_discord_token
TARGET_CHANNEL_ID=123456789012345678
```

## Step 4: Scrape Knowledge Base

```bash
python main.py scrape https://docs.learnbittensor.org --recursive --max-depth 2 --collection learn_bittensor_understand_bittensor
```

## Step 5: Run Atlas

```bash
python run_bot.py
```

## Step 6: Invite Atlas to Your Server

1. Go to Discord Developer Portal
2. Your App → OAuth2 → URL Generator
3. Select scopes: `bot`
4. Select permissions:
   - Send Messages
   - Read Messages
   - Read Message History
5. Copy URL and open in browser
6. Add Atlas to your server

## Troubleshooting

**Bot doesn't respond**:
- Check channel ID is correct
- Verify bot has permission to read/send messages
- Ensure Message Content Intent is enabled

**Error loading collection**:
- Make sure you scraped the knowledge base first
- Check collection name matches in `agent/tools.py`

**API errors**:
- Verify your API keys are correct
- Check you have enough API quota

## Commands

Once Atlas is running, just ask questions in the designated channel:

```
What is Bittensor?
How does TAO token work?
Explain subnet registration
```

Atlas will use AI to answer based on the knowledge base!
