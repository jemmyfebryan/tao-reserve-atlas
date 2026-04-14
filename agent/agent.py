"""
ReAct-style AI Agent using LangGraph.

This agent can reason about user questions and use tools to answer them.
"""
import json
import re
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from config import Config
from agent.tools import get_all_tools, get_tools_description
from agent.prompts import AGENT_SYSTEM_PROMPT


class BittensorAgent:
    """
    ReAct-style agent for answering questions about Bittensor.

    The agent can:
    - Reason about which tool to use
    - Execute tools to retrieve information
    - Synthesize answers from tool results
    """

    def __init__(self, model: str = "models/gemini-2.5-flash"):
        """
        Initialize the agent.

        Args:
            model: Gemini model to use
        """
        self.model_name = model
        self.tools = get_all_tools()
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(model)

    def _format_tools_for_agent(self) -> str:
        """Format tools description for the agent's system prompt."""
        return get_tools_description()

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """
        Extract JSON from text, handling markdown code blocks and extra content.

        Args:
            text: Text that may contain JSON

        Returns:
            Parsed JSON dict
        """
        # Try to extract JSON from markdown code blocks
        json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        match = re.search(json_pattern, text, re.DOTALL)

        if match:
            text = match.group(1)

        # Try to find JSON object in the text
        obj_pattern = r'\{[^{}]*"tool_name"[^{}]*"query"[^{}]*\}'
        match = re.search(obj_pattern, text, re.DOTALL)

        if match:
            text = match.group(0)

        return json.loads(text)

    def _select_tool(self, question: str) -> tuple[str, str]:
        """
        Select the appropriate tool and query for the user's question.

        Args:
            question: User's question

        Returns:
            Tuple of (tool_name, query)
        """
        tools_desc = self._format_tools_for_agent()

        # Use LLM to select tool
        selection_prompt = f"""Available tools:
{tools_desc}

User question: {question}

You are a tool selector. Your job is to:
1. Choose the BEST tool for answering this question
2. Formulate a specific query for that tool

Respond ONLY in this JSON format (no markdown, no extra text):
{{
    "tool_name": "name_of_the_tool",
    "query": "specific question to ask the tool"
}}

Choose the most relevant tool. If no tool is relevant, return {{"tool_name": "none", "query": "{question}"}}
"""

        try:
            response = self.model.generate_content(selection_prompt)
            result = self._extract_json(response.text)

            tool_name = result.get("tool_name", "none")
            query = result.get("query", question)

            # Validate tool exists
            if tool_name not in self.tools and tool_name != "none":
                tool_name = "none"

            return tool_name, query

        except Exception as e:
            print(f"Error in tool selection: {e}")
            print(f"Response was: {response.text if 'response' in locals() else 'N/A'}")
            return "none", question

    def _execute_tool(self, tool_name: str, query: str) -> Dict[str, Any]:
        """
        Execute a tool with the given query.

        Args:
            tool_name: Name of the tool to execute
            query: Query to send to the tool

        Returns:
            Tool execution result
        """
        if tool_name == "none" or tool_name not in self.tools:
            # Use Gemini for general questions
            from agent.prompts import GENERAL_CONVERSATION_PROMPT

            general_prompt = GENERAL_CONVERSATION_PROMPT.format(user_message=query)

            try:
                response = self.model.generate_content(general_prompt)
                return {
                    "tool_used": "general",
                    "answer": response.text,
                    "question": query,
                    "success": True,
                }
            except Exception as e:
                return {
                    "tool_used": "none",
                    "answer": f"Hey! I'm Atlas, here to help with the Tao Reserve community! I can answer questions about Bittensor, TAO, mining, and subnet development. What would you like to know?",
                    "question": query,
                    "success": False,
                }

        tool = self.tools[tool_name]
        return tool(query)

    def _synthesize_answer(
        self,
        question: str,
        tool_result: Dict[str, Any],
    ) -> str:
        """
        Synthesize a final answer based on the tool result.

        Args:
            question: Original user question
            tool_result: Result from tool execution

        Returns:
            Final answer string
        """
        tool_name = tool_result.get("tool_used", "none")
        answer = tool_result.get("answer", "")

        # If tool failed or returned none, return as-is
        if tool_name == "none" or not tool_result.get("success", False):
            return answer

        # For successful RAG queries, return the answer directly
        # (it's already formatted by the RAG tool)
        return answer

    def query(self, question: str) -> Dict[str, Any]:
        """
        Process a user question through the agent.

        Args:
            question: User's question

        Returns:
            Dictionary with the answer and metadata
        """
        # Step 1: Select the appropriate tool
        tool_name, query = self._select_tool(question)

        # Step 2: Execute the tool
        tool_result = self._execute_tool(tool_name, query)

        # Step 3: Synthesize the final answer
        final_answer = self._synthesize_answer(question, tool_result)

        return {
            "question": question,
            "answer": final_answer,
            "tool_used": tool_result.get("tool_used", "none"),
            "success": tool_result.get("success", False),
        }

    def query_simple(self, question: str) -> str:
        """
        Simple query interface that returns just the answer string.

        Args:
            question: User's question

        Returns:
            Answer string
        """
        result = self.query(question)
        return result["answer"]


# Convenience function for quick usage
def ask_agent(question: str, model: str = "models/gemini-2.5-flash") -> str:
    """
    Ask the agent a question and get the answer.

    Args:
        question: Question to ask
        model: Gemini model to use

    Returns:
        Answer string
    """
    agent = BittensorAgent(model=model)
    return agent.query_simple(question)
