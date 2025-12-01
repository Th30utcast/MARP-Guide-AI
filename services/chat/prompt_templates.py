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

    for idx, chunk in enumerate(chunks, start=1):
        # Format chunk with numbered citation marker
        chunk_text = f"[{idx}] Source: {chunk.get('title', 'Unknown')} - Page {chunk.get('page', 'N/A')}\n{chunk.get('text', '')}"
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
- If the context doesn't contain enough information to answer the question, say so clearly WITHOUT including any citation numbers
- CRITICAL: When stating a fact, immediately follow it with an inline citation number in square brackets [1], [2], etc., matching the numbered sources in the context
- IMPORTANT: Try to provide comprehensive answers that draw from MULTIPLE sources when relevant - aim for at least 3 different sources when possible
- If multiple sources contain related information, include details from each and cite them separately
- ONLY cite sources you actually use - do not mention sources you don't reference
- Each sentence or claim should have a citation to the specific source it came from
- Be concise but thorough
- Use academic language appropriate for university regulations

EXAMPLE FORMAT FOR ANSWERS WITH INFORMATION:
"Students must inform their department within 48 hours of an exam [1]. Medical certificates are required for illnesses over 5 days [2]. The Exceptional Circumstances Committee will review all claims [3]. For chronic conditions, medical practitioners must comment on assessment impact [4]."

EXAMPLE FORMAT FOR INSUFFICIENT INFORMATION:
"The provided context does not contain information about [topic]. Please try rephrasing your question or ask about MARP regulations."
"""

    # Build context from chunks with token management
    context_text = build_rag_context(context_chunks)

    # Combine into full prompt
    prompt = f"""{system_instruction}

CONTEXT:
{context_text}

QUESTION: {query}

ANSWER:"""

    return prompt
