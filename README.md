# TaoReserve Bot - Web Scraper Module

A flexible web scraping and vector database module for building RAG (Retrieval-Augmented Generation) knowledge bases. Designed for the TaoReserve Discord bot but usable as a standalone tool.

## Features

- 🕷️ **Web Scraping**: Scrape static websites with optional recursive link following
- 📦 **Vector Storage**: Local ChromaDB for persistent embedding storage
- 🔍 **Semantic Search**: Query your knowledge base with natural language
- 🛠️ **Dual Mode**: Use as CLI tool or import as Python module
- 🧩 **Bot-Ready**: Designed for easy integration with LangGraph/LangChain

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

The module is designed for easy integration with your LangGraph-based Discord bot:

```python
from langchain.tools import tool
from scraper import VectorStore

# Initialize vector store
vector_store = VectorStore(collection_name="bittensor_knowledge")
vector_store.load_existing_index()

@tool
def search_knowledge_base(query: str) -> str:
    """Search the Bittensor knowledge base for information."""
    results = vector_store.query(query, top_k=3)

    if not results:
        return "No relevant information found in the knowledge base."

    # Format results for the bot
    response = f"Found {len(results)} relevant results:\n\n"
    for i, result in enumerate(results, 1):
        response += f"{i}. {result['text'][:300]}...\n"
        response += f"   Source: {result['metadata']['url']}\n\n"

    return response

# Add this tool to your LangGraph agent
```

## Project Structure

```
taoreserve_bot/
├── scraper/
│   ├── __init__.py           # Package initialization
│   ├── web_scraper.py        # Web scraping logic
│   ├── vector_store.py       # Vector database operations
│   ├── document_processor.py # Content processing & chunking
│   └── cli.py               # Command-line interface
├── config.py                # Configuration management
├── main.py                  # CLI entry point
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
