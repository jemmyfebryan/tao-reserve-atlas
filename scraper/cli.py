"""
Command-line interface for the web scraper.
"""
import click
from rich.console import Console
from rich.table import Table
from scraper.web_scraper import WebScraper
from scraper.vector_store import VectorStore
from config import Config

console = Console()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """
    TaoReserve Bot Web Scraper - Scrape websites and build vector knowledge bases.

    Use this tool to scrape websites like learnbittensor.com and store the content
    in a local vector database for RAG-based AI responses.
    """
    try:
        Config.validate()
        Config.ensure_directories()
    except ValueError as e:
        console.print(f"[red]Configuration Error:[/red] {e}")
        raise click.Abort()


@cli.command()
@click.argument("url")
@click.option(
    "--collection", "-c",
    default="knowledge_base",
    help="Name for the vector collection",
)
@click.option(
    "--recursive", "-r",
    is_flag=True,
    help="Follow links recursively",
)
@click.option(
    "--max-depth", "-d",
    default=1,
    type=int,
    help="Maximum depth for recursive scraping (default: 1)",
)
@click.option(
    "--max-pages", "-p",
    default=100,
    type=int,
    help="Maximum number of pages to scrape",
)
@click.option(
    "--chunk-size",
    default=1024,
    type=int,
    help="Text chunk size in characters",
)
@click.option(
    "--chunk-overlap",
    default=128,
    type=int,
    help="Overlap between chunks",
)
def scrape(url, collection, recursive, max_depth, max_pages, chunk_size, chunk_overlap):
    """
    Scrape a website and store it in the vector database.

    Example:
        python main.py scrape https://learnbittensor.com --recursive --max-depth 2
    """
    console.print(f"[bold blue]Starting web scrape...[/bold blue]")
    console.print(f"URL: {url}")
    console.print(f"Recursive: {recursive}")
    console.print(f"Max Depth: {max_depth}")
    console.print(f"Max Pages: {max_pages}")
    console.print(f"Collection: {collection}\n")

    # Initialize scraper
    with WebScraper(
        max_pages=max_pages,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    ) as scraper:
        # Scrape the website
        chunks = scraper.scrape_url(
            url=url,
            recursive=recursive,
            max_depth=max_depth,
        )

    if not chunks:
        console.print("[yellow]No content was scraped.[/yellow]")
        return

    # Store in vector database
    console.print(f"\n[bold blue]Storing {len(chunks)} chunks in vector database...[/bold blue]")

    vector_store = VectorStore(collection_name=collection)

    # Load existing index if collection exists (to append instead of overwrite)
    existing_count = vector_store.collection.count()
    if existing_count > 0:
        console.print(f"[yellow]Found existing collection with {existing_count} documents. Appending...[/yellow]")
        vector_store.load_existing_index()

    vector_store.add_documents(chunks)

    # Show stats
    stats = vector_store.get_stats()
    console.print(f"\n[green]✓[/green] Scraping complete!")
    console.print(f"  Documents stored: {stats['document_count']}")
    console.print(f"  Collection: {stats['collection_name']}")
    console.print(f"  Database location: {stats['persist_directory']}")


@cli.command()
@click.argument("query")
@click.option(
    "--collection", "-c",
    default="knowledge_base",
    help="Collection to query",
)
@click.option(
    "--top-k", "-k",
    default=3,
    type=int,
    help="Number of results to return",
)
def query(query, collection, top_k):
    """
    Query the vector database (retrieves chunks only).

    Example:
        python main.py query "What is Bittensor?"
    """
    vector_store = VectorStore(collection_name=collection)

    # Try to load existing index
    if not vector_store.load_existing_index():
        console.print("[yellow]No existing index found. Collection may be empty.[/yellow]")
        return

    # Query and display results
    vector_store.pretty_query(query, top_k=top_k)


@cli.command()
@click.argument("question")
@click.option(
    "--collection", "-c",
    default="knowledge_base",
    help="Collection to query",
)
@click.option(
    "--top-k", "-k",
    default=5,
    type=int,
    help="Number of relevant chunks to retrieve for context",
)
@click.option(
    "--model", "-m",
    default="models/gemini-2.5-flash",
    help="Gemini model to use for answering (default: gemini-2.5-flash)",
)
def ask(question, collection, top_k, model):
    """
    Ask a question using AI with knowledge from the collection (RAG).

    This retrieves relevant chunks and uses Gemini to answer your question.

    Example:
        python main.py ask "What is Bittensor and how does it work?"

    For more detailed answers, increase top_k:
        python main.py ask "Explain TAO tokenomics" --top-k 10
    """
    vector_store = VectorStore(collection_name=collection)

    # Try to load existing index
    if not vector_store.load_existing_index():
        console.print("[yellow]No existing index found. Collection may be empty.[/yellow]")
        return

    # Ask and display answer
    vector_store.pretty_ask(question, top_k=top_k, model=model)


@cli.command()
@click.option(
    "--collection", "-c",
    default="knowledge_base",
    help="Collection to inspect",
)
def stats(collection):
    """Display statistics about a collection."""
    vector_store = VectorStore(collection_name=collection)

    # Try to get stats
    try:
        vector_store.load_existing_index()
        stats_data = vector_store.get_stats()

        table = Table(title=f"Collection Stats: {collection}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Name", stats_data["collection_name"])
        table.add_row("Documents", str(stats_data["document_count"]))
        table.add_row("Location", stats_data["persist_directory"])

        console.print(table)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


@cli.command()
@click.option(
    "--collection", "-c",
    default="knowledge_base",
    help="Collection to delete",
)
@click.option(
    "--confirm",
    is_flag=True,
    help="Skip confirmation prompt",
)
def delete(collection, confirm):
    """
    Delete a collection from the database.

    Warning: This cannot be undone!
    """
    if not confirm:
        click.confirm(
            f"Are you sure you want to delete collection '{collection}'?",
            abort=True,
        )

    vector_store = VectorStore(collection_name=collection)
    vector_store.delete_collection()
    console.print(f"[green]✓[/green] Collection '{collection}' deleted")


@cli.command()
@click.argument("old_name")
@click.argument("new_name")
@click.option(
    "--confirm",
    is_flag=True,
    help="Skip confirmation prompt",
)
def rename(old_name, new_name, confirm):
    """
    Rename a collection.

    Example:
        python main.py rename knowledge_base learn_bittensor
    """
    if not confirm:
        click.confirm(
            f"Rename collection '{old_name}' to '{new_name}'?",
            abort=True,
        )

    vector_store = VectorStore(collection_name=old_name)
    vector_store.rename_collection(new_name)
    console.print(f"[green]✓[/green] Collection renamed from '{old_name}' to '{new_name}'")


@cli.command()
def collections():
    """List all collections in the database."""
    import chromadb
    from chromadb.config import Settings

    client = chromadb.PersistentClient(
        path=Config.CHROMA_PERSIST_DIR,
        settings=Settings(anonymized_telemetry=False),
    )

    collections = client.list_collections()

    if not collections:
        console.print("[yellow]No collections found.[/yellow]")
        return

    table = Table(title="Collections")
    table.add_column("Name", style="cyan")
    table.add_column("Documents", style="green")

    for coll in collections:
        table.add_row(coll.name, str(coll.count()))

    console.print(table)


if __name__ == "__main__":
    cli()
