# TaoReserve Bot - Web Scraper & AI Agent

A flexible web scraping, vector database, and AI agent system for building RAG (Retrieval-Augmented Generation) knowledge bases. Designed for the TaoReserve Discord bot but usable as a standalone tool.

## Features

- 🕷️ **Web Scraping**: Scrape static websites with optional recursive link following
- 📦 **Vector Storage**: Local ChromaDB for persistent embedding storage
- 🔍 **Semantic Search**: Query your knowledge base with natural language
- 🤖 **AI Agent**: ReAct-style agent that uses tools to answer questions
- 🛠️ **Dual Mode**: Use as CLI tool or import as Python module
- 🧩 **Bot-Ready**: Designed for easy integration with Discord bots

## Installation

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env and add your Google Gemini API key
# Get one from: https://makersuite.google.com/app/apikey
```

## Usage

### As a CLI Tool

**Scrape a website:**
```bash
python main.py scrape https://learnbittensor.com --recursive --max-depth 2
```

**Query the knowledge base:**
```bash
python main.py query "What is Bittensor?"
```

**View collection stats:**
```bash
python main.py stats --collection knowledge_base
```

**List all collections:**
```bash
python main.py collections
```

**Delete a collection:**
```bash
python main.py delete --collection knowledge_base
```

**Ask AI (RAG with context):**
```bash
python main.py ask "What is Bittensor and how does it work?"
```

**Rename a collection:**
```bash
python main.py rename knowledge_base learn_bittensor
```

### AI Agent

The agent uses tools to answer questions intelligently:

```python
from agent import ask_agent

# Simple usage
answer = ask_agent("What is TAO token?")
print(answer)

# Advanced usage
from agent import BittensorAgent

agent = BittensorAgent()
result = agent.query("Explain subnet registration")

print(f"Tool used: {result['tool_used']}")
print(f"Answer: {result['answer']}")
```

**Test the agent:**
```bash
python test_agent.py
```

### Adding New Tools

Tools are defined in `agent/tools.py`. To add a new tool:

```python
# In agent/tools.py, add to get_all_tools():
"my_new_tool": RAGTool(
    collection_name="my_collection",
    name="my_new_tool",
    description="Use this for questions about..."
),
```

That's it! The agent will automatically discover and use the new tool.

### As a Python Module

```python
from scraper import WebScraper, VectorStore

# Scrape a website
scraper = WebScraper(max_pages=100)
chunks = scraper.scrape_url(
    "https://learnbittensor.com",
    recursive=True,
    max_depth=2,
)
scraper.close()

# Store in vector database
vector_store = VectorStore(collection_name="bittensor_knowledge")
vector_store.add_documents(chunks)

# Query the knowledge base
results = vector_store.query("What is TAO?", top_k=5)

for result in results:
    print(f"Score: {result['score']}")
    print(f"URL: {result['metadata']['url']}")
    print(f"Content: {result['text'][:200]}...")
```

## Integration with Discord Bot

The agent is designed for easy Discord bot integration:

```python
from agent import BittensorAgent

# Initialize agent once
agent = BittensorAgent()

# In your Discord message handler
async def on_message(message):
    if message.content.startswith('!ask'):
        question = message.content[5:].strip()

        # Get answer from agent
        answer = agent.query_simple(question)

        # Send to Discord
        await message.channel.send(answer)
```

Or use the simpler interface:

```python
from agent import ask_agent

# In your Discord bot
async def handle_question(question: str) -> str:
    return ask_agent(question)
```

The agent automatically:
1. Selects the right tool based on the question
2. Queries the knowledge base
3. Returns a natural, friendly answer
4. No citations or technical artifacts - just clean answers!

## Project Structure

```
taoreserve_bot/
├── scraper/
│   ├── __init__.py           # Package initialization
│   ├── web_scraper.py        # Web scraping logic
│   ├── vector_store.py       # Vector database operations
│   ├── document_processor.py # Content processing & chunking
│   ├── gemini_embeddings.py  # Gemini embeddings wrapper
│   └── cli.py               # Command-line interface
├── agent/
│   ├── __init__.py           # Agent package
│   ├── agent.py             # ReAct-style agent implementation
│   ├── tools.py             # Tool definitions (easy to add new tools!)
│   └── prompts.py           # System prompts
├── config.py                # Configuration management
├── main.py                  # CLI entry point
├── test_agent.py            # Test script for agent
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## Configuration

Edit `.env` file to configure:

- `GEMINI_API_KEY`: Required for embeddings (get from https://makersuite.google.com/app/apikey)
- `CHROMA_PERSIST_DIR`: Where to store the vector database
- `SCRAPER_USER_AGENT`: User agent for web requests
- `SCRAPER_TIMEOUT`: Request timeout in seconds
- `SCRAPER_MAX_PAGES`: Maximum pages to scrape per run

## CLI Options

### `scrape` command
- `--collection, -c`: Collection name (default: knowledge_base)
- `--recursive, -r`: Follow links recursively
- `--max-depth, -d`: Maximum recursion depth (default: 1)
- `--max-pages, -p`: Maximum pages to scrape (default: 100)
- `--chunk-size`: Text chunk size in characters (default: 1024)
- `--chunk-overlap`: Overlap between chunks (default: 128)

### `query` command
- `--collection, -c`: Collection to query (default: knowledge_base)
- `--top-k, -k`: Number of results (default: 3)

## Tips for Scraping learnbittensor.com

1. **Start with specific pages** rather than the entire site:
   ```bash
   python main.py scrape https://learnbittensor.com/docs/introduction
   ```

2. **Use depth control** to avoid scraping too many pages:
   ```bash
   python main.py scrape https://learnbittensor.com --recursive --max-depth 1
   ```

3. **Create separate collections** for different topics:
   ```bash
   python main.py scrape https://learnbittensor.com/docs --collection docs
   python main.py scrape https://learnbittensor.com/blog --collection blog
   ```

## Troubleshooting

**Error: GEMINI_API_KEY is required**
- Make sure you've created a `.env` file with your Gemini API key from https://makersuite.google.com/app/apikey

**Scraping returns no content**
- The site might use JavaScript rendering. Try scraping specific pages rather than the root
- Check if the site blocks automated requests (check robots.txt)

**Poor query results**
- Try adjusting `--chunk-size` and `--chunk-overlap` when scraping
- Use more specific queries
- Consider scraping more pages for better coverage

## License

MIT
