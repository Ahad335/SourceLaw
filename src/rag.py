# The RAG pipeline: retrieve relevant law, then answer strictly from it.
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from src.config import MAX_DISTANCE, TOP_K
from src.llm import get_chat_model
from src.vectorstore import get_vectorstore

NO_CONTEXT_ANSWER = (
    "I couldn't find anything about that in the legal documents I have loaded. "
    "Try rephrasing, or ask about the Constitution, labour law, or social security."
)

SYSTEM_PROMPT = """You are an Indian legal assistant.

Rules:
- Answer ONLY from the context provided below.
- Do NOT make up laws or sections.
- Keep the answer simple and in plain English.
- Always cite the source document and page you used.

Context:
{context}
"""


def retrieve(question, k=TOP_K, max_distance=MAX_DISTANCE):
    """Return (documents, sources) for the question, filtered by distance."""
    docs_and_scores = get_vectorstore().similarity_search_with_score(question, k=k)

    docs, sources = [], []
    for doc, score in docs_and_scores:
        if float(score) > max_distance:  # lower distance = better match
            continue
        docs.append(doc)
        sources.append(
            {
                "source": doc.metadata.get("source", "Unknown"),
                "page": doc.metadata.get("page", 0),
                "category": doc.metadata.get("category", "general"),
                "score": round(float(score), 4),
                "excerpt": doc.page_content[:400].strip(),
            }
        )
    return docs, sources


def build_context(docs):
    parts = []
    for doc in docs:
        source = doc.metadata.get("source", "Unknown")
        page = doc.metadata.get("page", "N/A")
        parts.append(f"[Source: {source}, Page: {page}]\n{doc.page_content}")
    return "\n\n".join(parts)


def to_messages(history):
    """Convert the frontend's [{role, content}] history into LangChain messages."""
    messages = []
    for turn in history or []:
        content = (turn.get("content") or "").strip()
        if not content:
            continue
        if turn.get("role") == "assistant":
            messages.append(AIMessage(content=content))
        else:
            messages.append(HumanMessage(content=content))
    return messages


def answer_question(question, history=None):
    """Full RAG turn. Returns {"answer": str, "sources": [...]}."""
    docs, sources = retrieve(question)

    if not docs:
        return {"answer": NO_CONTEXT_ANSWER, "sources": []}

    messages = [SystemMessage(content=SYSTEM_PROMPT.format(context=build_context(docs)))]
    messages += to_messages(history)
    messages.append(HumanMessage(content=question))

    result = get_chat_model().invoke(messages)
    return {"answer": result.content, "sources": sources}
