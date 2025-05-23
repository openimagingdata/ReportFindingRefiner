# src/reportfindingrefiner/llm_query.py
from typing import List
from ollama import chat, ChatResponse
from reportfindingrefiner.config import DEFAULT_MODEL # type: ignore

def build_query(query: str, context: List[str]) -> str:
    """
    Combine the question and the documents into a single prompt string.
    """
    prompt = f"""
    You are a helpful assistant. Use the following context to answer the question.

    Context:
    {context}

    Question: {query}

    Answer:
    """
    return prompt

#NOTE: assumes user has ollama installed and running and serving the model
def query_llm(query: str, context: List[str], model: str = DEFAULT_MODEL) -> str:
    """
    Queries an Ollama LLM with a constructed prompt and returns a string response.
    """
    prompt = build_query(query, context)
    response: ChatResponse = chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.message.content