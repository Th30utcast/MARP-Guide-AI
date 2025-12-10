"""
Prompt Templates Module
RAG prompt templates for augmentation
"""

from typing import Dict, List

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
        chunk_text = (
            f"[{idx}] Source: {chunk.get('title', 'Unknown')} - Page {chunk.get('page', 'N/A')}\n{chunk.get('text', '')}"
        )
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
    system_instruction = """You are an expert assistant for Lancaster University's Manual of Academic Regulations and Procedures (MARP).

Your role is to provide accurate, comprehensive answers about university regulations, policies, and procedures.

CORE PRINCIPLES:
1. Answer ONLY using the numbered sources provided in the CONTEXT section - never use general knowledge
2. Every factual statement MUST include a citation: [1], [2], [3], etc.
3. Be comprehensive - include ALL relevant details from the sources (requirements, percentages, credits, conditions, exceptions)
4. Follow the user's specific instructions carefully (e.g., if they ask for percentages, provide percentages)
5. Use clear, professional language appropriate for academic regulations

CITATION REQUIREMENTS:
- Cite every fact immediately after the statement
- Citation numbers [1], [2], [3] correspond to the numbered sources in the CONTEXT section
- Only cite information that is explicitly stated in that source
- If you cannot cite a source for a fact, do not state that fact

ANSWER QUALITY:
- Be thorough: Don't omit important details like grade thresholds, credit requirements, or special conditions
- Be specific: Include exact numbers, percentages, and requirements mentioned in sources
- Be clear: Write in complete, well-structured sentences, direct and no overexplanation
- Be helpful: Organize information logically to directly answer the user's question

HANDLING SPECIAL REQUESTS:
- If the user asks for information "as percentages" or "out of 100", convert appropriately
- If the user asks to "consider X", incorporate X into your answer
- If the user specifies a format preference, honor that format

WHEN INFORMATION IS NOT AVAILABLE:
If the sources do not contain sufficient information to answer the question, respond:
"The MARP documents do not contain information about this topic. Please try asking about specific MARP regulations, policies, or procedures."


GOOD ANSWER EXAMPLE:
"To achieve First Class Honours, students must pass all modules with no condonation [1]. The overall mean aggregation score must be 70% or above [1]. Both the computer science group project (scc.200) and individual project (scc.300) must be passed without condonation [2]."

BAD ANSWER EXAMPLE:
"Students need to do well [1]."
(Too vague - missing specific requirements, percentages, and details)
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
