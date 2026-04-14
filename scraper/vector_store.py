"""
Vector store for managing embeddings and similarity search.
"""
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from tqdm import tqdm
import chromadb
from chromadb.config import Settings
from llama_index.core import VectorStoreIndex, Document, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from scraper.gemini_embeddings import GeminiEmbedding
from config import Config
import google.generativeai as genai


class VectorStore:
    """Vector database for storing and querying document embeddings."""

    def __init__(
        self,
        collection_name: str = "knowledge_base",
        persist_directory: Optional[str] = None,
        embedding_model: Optional[str] = None,
    ):
        """
        Initialize the vector store.

        Args:
            collection_name: Name of the collection in ChromaDB
            persist_directory: Directory to persist the database
            embedding_model: Model name for embeddings
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory or Config.CHROMA_PERSIST_DIR
        self.embedding_model = embedding_model or Config.EMBEDDING_MODEL

        # Ensure directory exists
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)

        # Initialize embedding model (Google Gemini)
        self.embed_model = GeminiEmbedding(
            model_name=self.embedding_model,
            api_key=Config.GEMINI_API_KEY,
        )

        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False),
        )

        # Get or create collection
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

        # Initialize vector store for LlamaIndex
        self.vector_store = ChromaVectorStore(chroma_collection=self.collection)
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)

        self.index: Optional[VectorStoreIndex] = None

    def add_documents(self, chunks: List[Dict[str, Any]], show_progress: bool = True) -> int:
        """
        Add document chunks to the vector store.

        Args:
            chunks: List of document chunks with 'text' and 'metadata' keys
            show_progress: Whether to show progress bar

        Returns:
            Number of documents added
        """
        if not chunks:
            print("No chunks to add")
            return 0

        # Convert to LlamaIndex Documents
        documents = []
        for chunk in chunks:
            doc = Document(
                text=chunk["text"],
                metadata=chunk["metadata"],
            )
            documents.append(doc)

        # Create index from documents
        if show_progress:
            print(f"Creating embeddings for {len(documents)} chunks...")
            with tqdm(total=len(documents), desc="Embedding documents") as pbar:
                # Update progress manually by processing in batches
                batch_size = 10
                for i in range(0, len(documents), batch_size):
                    batch = documents[i:i + batch_size]
                    if self.index is None:
                        self.index = VectorStoreIndex.from_documents(
                            batch,
                            storage_context=self.storage_context,
                            embed_model=self.embed_model,
                            show_progress=False,
                        )
                    else:
                        # Insert into existing index
                        for doc in batch:
                            self.index.insert(doc)
                    pbar.update(len(batch))
        else:
            self.index = VectorStoreIndex.from_documents(
                documents,
                storage_context=self.storage_context,
                embed_model=self.embed_model,
            )

        print(f"Successfully added {len(documents)} chunks to vector store")
        return len(documents)

    def load_existing_index(self) -> bool:
        """
        Load existing index from the vector store.

        Returns:
            True if index was loaded successfully
        """
        try:
            self.index = VectorStoreIndex.from_vector_store(
                vector_store=self.vector_store,
                storage_context=self.storage_context,
                embed_model=self.embed_model,
            )
            print(f"Loaded existing index with {self.collection.count()} documents")
            return True
        except Exception as e:
            print(f"Could not load existing index: {e}")
            return False

    def query(
        self,
        query_text: str,
        top_k: int = 5,
        similarity_threshold: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Query the vector store for similar documents.

        Args:
            query_text: Query text
            top_k: Number of results to return
            similarity_threshold: Minimum similarity score (0-1)

        Returns:
            List of relevant documents with metadata and scores
        """
        if self.index is None:
            raise ValueError("Index not initialized. Call add_documents() or load_existing_index() first.")

        # Use retriever directly (no LLM needed)
        retriever = self.index.as_retriever(
            similarity_top_k=top_k,
        )

        # Execute query
        nodes = retriever.retrieve(query_text)

        # Format results
        results = []
        for node in nodes:
            result = {
                "text": node.node.text,
                "metadata": node.node.metadata,
                "score": node.score if hasattr(node, "score") else None,
            }

            # Filter by similarity threshold if provided
            if similarity_threshold is None or result["score"] >= similarity_threshold:
                results.append(result)

        return results

    def delete_collection(self) -> None:
        """Delete the entire collection from the database."""
        self.chroma_client.delete_collection(self.collection_name)
        print(f"Deleted collection: {self.collection_name}")
        self.index = None

    def rename_collection(self, new_name: str) -> bool:
        """
        Rename a collection by copying to a new collection and deleting the old one.

        Args:
            new_name: New name for the collection

        Returns:
            True if successful
        """
        try:
            # Get all data from old collection
            count = self.collection.count()
            if count == 0:
                print(f"Collection '{self.collection_name}' is empty")
                return False

            print(f"Copying {count} documents from '{self.collection_name}' to '{new_name}'...")

            # Get all data
            results = self.collection.get(include=["embeddings", "documents", "metadatas"])

            # Create new collection
            new_collection = self.chroma_client.create_collection(
                name=new_name,
                metadata={"hnsw:space": "cosine"},
            )

            # Add all data to new collection
            if results["embeddings"]:
                new_collection.add(
                    embeddings=results["embeddings"],
                    documents=results["documents"],
                    metadatas=results["metadatas"],
                    ids=results["ids"],
                )

            # Delete old collection
            self.chroma_client.delete_collection(self.collection_name)

            # Update instance variables
            self.collection_name = new_name
            self.collection = new_collection
            self.vector_store = ChromaVectorStore(chroma_collection=self.collection)
            self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
            self.index = None

            print(f"✓ Successfully renamed '{self.collection_name}' to '{new_name}'")
            return True

        except Exception as e:
            print(f"Error renaming collection: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store.

        Returns:
            Dictionary with collection statistics
        """
        return {
            "collection_name": self.collection_name,
            "document_count": self.collection.count(),
            "persist_directory": self.persist_directory,
        }

    def pretty_query(self, query_text: str, top_k: int = 3) -> None:
        """
        Print query results in a readable format.

        Args:
            query_text: Query text
            top_k: Number of results to return
        """
        results = self.query(query_text, top_k=top_k)

        print(f"\n{'='*60}")
        print(f"Query: {query_text}")
        print(f"{'='*60}\n")

        for i, result in enumerate(results, 1):
            print(f"Result {i}:")
            print(f"  Score: {result['score']:.4f}" if result['score'] else "  Score: N/A")
            print(f"  URL: {result['metadata'].get('url', 'N/A')}")
            print(f"  Title: {result['metadata'].get('title', 'N/A')}")
            print(f"  Content: {result['text'][:800]}...")  # Show more content
            print()

    def ask(
        self,
        question: str,
        top_k: int = 5,
        model: str = "models/gemini-2.5-flash",
    ) -> Dict[str, Any]:
        """
        Ask a question using AI with retrieved context from the vector store.

        Args:
            question: The question to answer
            top_k: Number of relevant chunks to retrieve
            model: Gemini model to use for answering (default: gemini-2.0-flash-exp)

        Returns:
            Dictionary with answer, sources, and metadata
        """
        """
        Ask a question using AI with retrieved context from the vector store.

        Args:
            question: The question to answer
            top_k: Number of relevant chunks to retrieve
            model: Gemini model to use for answering

        Returns:
            Dictionary with answer, sources, and metadata
        """
        if self.index is None:
            raise ValueError("Index not initialized. Call add_documents() or load_existing_index() first.")

        # Retrieve relevant chunks
        retriever = self.index.as_retriever(similarity_top_k=top_k)
        nodes = retriever.retrieve(question)

        if not nodes:
            return {
                "answer": "I couldn't find any relevant information in the knowledge base to answer your question.",
                "sources": [],
                "question": question,
            }

        # Build context from retrieved chunks
        context_parts = []
        sources = []

        for i, node in enumerate(nodes, 1):
            text = node.node.text
            metadata = node.node.metadata
            url = metadata.get("url", "N/A")
            title = metadata.get("title", "N/A")

            context_parts.append(f"[Source {i}] {title}\n{text}\n")
            sources.append({
                "url": url,
                "title": title,
                "score": node.score if hasattr(node, "score") else None,
            })

        context = "\n".join(context_parts)

        # Create prompt for Gemini
        prompt = f"""You are a helpful assistant answering questions based on the provided context from the knowledge base.

CONTEXT:
{context}

QUESTION: {question}

INSTRUCTIONS:
- Answer the question using ONLY the information from the context above
- If the context doesn't contain enough information, say so
- Be specific and cite sources using [Source X] references
- If information conflicts between sources, mention it
- Keep answers clear and concise

ANSWER:"""

        # Generate answer using Gemini
        try:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            gemini_model = genai.GenerativeModel(model)
            response = gemini_model.generate_content(prompt)

            answer = response.text

            return {
                "answer": answer,
                "sources": sources,
                "question": question,
                "model": model,
            }

        except Exception as e:
            return {
                "answer": f"Error generating answer: {e}",
                "sources": sources,
                "question": question,
            }

    def pretty_ask(self, question: str, top_k: int = 5, model: str = "models/gemini-2.5-flash") -> None:
        """
        Ask a question and print the answer in a readable format.

        Args:
            question: The question to answer
            top_k: Number of relevant chunks to retrieve
            model: Gemini model to use
        """
        result = self.ask(question, top_k=top_k, model=model)

        print(f"\n{'='*70}")
        print(f"Question: {result['question']}")
        print(f"{'='*70}\n")

        print(f"Answer:\n{result['answer']}\n")

        if result['sources']:
            print(f"{'='*70}")
            print("Sources:")
            for i, source in enumerate(result['sources'], 1):
                print(f"\n{i}. {source['title']}")
                print(f"   URL: {source['url']}")
                if source['score']:
                    print(f"   Relevance: {source['score']:.4f}")
            print()
