"""
Migration Co-pilot module with AI chat and RAG system.

Provides intelligent migration assistance:
- AI-powered chat interface
- RAG-based knowledge retrieval
- Context-aware suggestions
- Migration pattern recommendations
- Interactive troubleshooting
"""

from .copilot_engine import MigrationCopilot
from .rag_system import RAGSystem
from .chat_interface import ChatInterface
from .knowledge_base import KnowledgeBase

__all__ = [
    'MigrationCopilot',
    'RAGSystem',
    'ChatInterface',
    'KnowledgeBase'
]
