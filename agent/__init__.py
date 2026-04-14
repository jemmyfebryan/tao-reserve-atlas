"""
AI Agent module for Discord bot using LangGraph ReAct pattern.

This module provides a modular agent system with tools for answering questions
using RAG (Retrieval-Augmented Generation) from various knowledge bases.
"""
from agent.agent import BittensorAgent, ask_agent
from agent.tools import get_all_tools

__all__ = ["BittensorAgent", "ask_agent", "get_all_tools"]
