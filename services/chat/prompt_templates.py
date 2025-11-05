"""
Prompt Templates Module
RAG prompt templates for augmentation 
"""
from typing import List, Dict
import config

def estimate_tokens(text: str) -> int:
    """
    Simple token estimation (roughly 4 chars per token)

    Args:
        text: Input text

    Returns:
        Estimated token count
    """
    return len(text) // 4

def build_rag_context(chunks: List[Dict], max_tokens: int = None) -> str:
    """
    Build context string from retrieved chunks with token limit management

    Args:
        chunks: List of retrieved chunks with metadata
        max_tokens: Maximum tokens for context (defaults to config)

    Returns:
        Formatted context string
    """
    max_tokens = max_tokens or config.MAX_CONTEXT_TOKENS
    context_parts = []
    current_tokens = 0

    for chunk in chunks:
        # Format chunk with metadata
        chunk_text = f"[Source: {chunk.get('title', 'Unknown')} - Page {chunk.get('page', 'N/A')}]\n{chunk.get('text', '')}"
        chunk_tokens = estimate_tokens(chunk_text)

        # Check if adding this chunk would exceed limit
        if current_tokens + chunk_tokens > max_tokens:
            break

        context_parts.append(chunk_text)
        current_tokens += chunk_tokens

    return "\n\n---\n\n".join(context_parts)

def create_rag_prompt(query: str, context_chunks: List[Dict]) -> str:
    """
    Create RAG prompt by combining system instructions, context, and user query

    Args:
        query: User's question
        context_chunks: List of retrieved chunks with metadata

    Returns:
        Complete RAG prompt string
    """
    # System instructions
    system_instruction = """You are a helpful assistant that answers questions about Lancaster University's Manual of Academic Regulations and Procedures (MARP).

IMPORTANT INSTRUCTIONS:
- Answer questions ONLY based on the provided context
- If the context doesn't contain enough information to answer the question, say so
- Include specific references to sources in your answer (mention document titles and page numbers)
- Be concise and clear
- Use academic language appropriate for university regulations"""

    # Build context from chunks with token management
    context_text = build_rag_context(context_chunks)

    # Combine into full prompt
    prompt = f"""{system_instruction}

CONTEXT:
{context_text}

QUESTION: {query}

ANSWER:"""

    return prompt
