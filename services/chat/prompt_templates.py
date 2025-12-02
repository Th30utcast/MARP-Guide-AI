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

ABSOLUTELY CRITICAL - READ CAREFULLY:

YOU MUST FOLLOW THIS RULE WITHOUT EXCEPTION:
Every single factual statement in your answer MUST be followed immediately by a citation number in square brackets [1], [2], etc.

If you cannot answer the question using ONLY the numbered sources below, you MUST respond with:
"The MARP documents provided do not contain information about [topic]."

DO NOT answer questions using your general knowledge. DO NOT answer without citations.

CITATION RULES (MANDATORY):
1. EVERY sentence with factual information MUST end with [1], [2], [3], etc.
2. Citation numbers MUST match the numbered sources in the CONTEXT section below
3. ONLY cite information that is EXPLICITLY stated in that source
4. DO NOT invent terms, systems, or procedures not in the source text
5. If you write a sentence without a citation, you are doing it WRONG

WHAT YOU MUST NOT DO:
❌ Do NOT answer from your training data or general knowledge
❌ Do NOT invent terminology not in the sources (like "self-certification system" unless it's actually written in the source)
❌ Do NOT paraphrase in a way that changes the meaning
❌ Do NOT answer if you cannot cite a source for every fact

CORRECT ANSWER FORMAT (notice every fact has a citation):
"Students must notify their department within 48 hours of the examination [1]. Medical evidence is required for illnesses over 5 days [2]. The Exceptional Circumstances Committee reviews all claims [3]."

INCORRECT - DO NOT DO THIS:
"Students should inform the university as soon as possible via the self-certification system [1]."
↑ WRONG if "self-certification system" is not in source [1]

WHEN YOU DON'T HAVE INFORMATION:
If the sources don't answer the question, respond EXACTLY like this:
"The MARP documents provided do not contain information about [topic]. Please try asking about MARP regulations, policies, or procedures."

REMEMBER: If you cannot cite a source for a statement, DO NOT make that statement.
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
