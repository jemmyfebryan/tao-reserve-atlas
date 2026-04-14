# Atlas Discord Bot - Quick Start

## What You Got

Atlas is an AI-powered Discord bot that:
- Answers questions about Bittensor using RAG
- Uses Gemini AI for intelligent responses
- Only responds in designated channels
- Handles long messages automatically

## File Structure

```
taoreserve_bot/
├── bot.py              # Main Discord bot (Atlas)
├── run_bot.py          # Quick start script
├── agent/              # AI agent system
│   ├── agent.py        # ReAct-style agent
│   ├── tools.py        # Tool definitions (add new tools here!)
│   └── prompts.py      # System prompts
├── scraper/            # Web scraper & vector DB
│   ├── vector_store.py # ChromaDB operations
│   └── ...
├── .env                # Your API keys (create this!)
└── .env.example        # Template
```

## 3 Quick Steps to Run Atlas

### 1. Configure API Keys
```bash
cp .env.example .env
# Edit .env and add:
# - GEMINI_API_KEY
# - DISCORD_TOKEN
# - TARGET_CHANNEL_ID
```

### 2. Scrape Knowledge Base
```bash
python main.py scrape https://docs.learnbittensor.org --recursive --max-depth 2 --collection learn_bittensor_understand_bittensor
```

### 3. Start Atlas
```bash
python run_bot.py
```

## How to Add New Tools

Edit `agent/tools.py`:

```python
"my_new_tool": RAGTool(
    collection_name="my_collection",
    name="my_new_tool",
    description="Use for questions about..."
),
```

That's it! Atlas will automatically use the new tool.

## Discord Setup

1. **Create Bot**: https://discord.com/developers/applications
2. **Enable**: Message Content Intent
3. **Invite**: With Send Messages, Read Messages permissions
4. **Channel**: Get channel ID (right-click → Copy ID)

See `SETUP.md` for detailed instructions.

## Features

- ✅ AI-powered responses
- ✅ RAG from knowledge base
- ✅ Channel-specific responses
- ✅ Typing indicator
- ✅ Long message handling
- ✅ Error recovery
- ✅ Modular tools

## Support

Check `SETUP.md` for troubleshooting and detailed setup.
