"""
Tools for the AI Agent.

Each tool represents a capability the agent can use. Tools are modular
and can be easily added or modified.
"""
from typing import Dict, Any
from scraper.vector_store import VectorStore
from config import Config


class RAGTool:
    """
    RAG (Retrieval-Augmented Generation) tool for querying knowledge bases.
    """

    def __init__(self, collection_name: str, name: str, description: str):
        """
        Initialize a RAG tool.

        Args:
            collection_name: Name of the ChromaDB collection
            name: Tool name (used by agent)
            description: Tool description (helps agent decide when to use it)
        """
        self.collection_name = collection_name
        self.name = name
        self.description = description

    def __call__(self, question: str) -> Dict[str, Any]:
        """
        Execute the tool - query the knowledge base and get an AI answer.

        Args:
            question: User's question

        Returns:
            Dictionary with answer and metadata
        """
        try:
            vector_store = VectorStore(collection_name=self.collection_name)
            vector_store.load_existing_index()

            result = vector_store.ask(question, top_k=5)

            return {
                "tool_used": self.name,
                "answer": result["answer"],
                "question": question,
                "success": True,
            }

        except Exception as e:
            return {
                "tool_used": self.name,
                "answer": f"Error querying knowledge base: {str(e)}",
                "question": question,
                "success": False,
            }


def get_all_tools() -> Dict[str, RAGTool]:
    """
    Get all available tools for the agent.

    To add a new tool:
    1. Create a new RAGTool instance with your collection
    2. Add it to this dictionary

    Returns:
        Dictionary mapping tool names to tool instances
    """
    tools = {
        "understand_bittensor": RAGTool(
            collection_name="learn_bittensor_understand_bittensor",
            name="understand_bittensor",
            description=(
                "Useful for answering questions about Bittensor, TAO token, "
                "mining, subnet registration, and general Bittensor concepts. "
                "Use this tool when users ask: 'What is Bittensor?', 'How does TAO work?', "
                "'Explain Bittensor mining', etc."
            ),
        ),
        # Add more tools here as you scrape more collections:
        # "bittensor_docs": RAGTool(
        #     collection_name="learn_bittensor_docs",
        #     name="bittensor_docs",
        #     description="Detailed technical documentation about Bittensor API and development."
        # ),
        # "bittensor_blog": RAGTool(
        #     collection_name="bittensor_blog",
        #     name="bittensor_blog",
        #     description="Latest news and updates from the Bittensor blog."
        # ),
    }

    return tools


def get_tools_description() -> str:
    """
    Get a formatted description of all available tools.

    Returns:
        String describing available tools
    """
    tools = get_all_tools()
    descriptions = []

    for tool_name, tool in tools.items():
        descriptions.append(f"- **{tool_name}**: {tool.description}")

    return "\n".join(descriptions)
