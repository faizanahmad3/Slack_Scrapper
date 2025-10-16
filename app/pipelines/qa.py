import logging
from typing import Dict

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from app.config import get_settings
from app.providers.registry import get_embeddings, get_llm
from app.vectorstore.qdrant_store import QdrantStore

logger = logging.getLogger(__name__)


RAG_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that answers questions using only the provided Slack channel context. If the answer is not in the context, say you don't know."),
    ("human", "Question: {question}\n\nContext:\n{context}"),
])


def _format_docs(docs):
    return "\n\n".join(f"[{i+1}] {d.page_content}" for i, d in enumerate(docs))


def answer_question(channel: str, question: str, k: int = 5) -> Dict:
    logger.info(f"Starting QA for channel '{channel}', question: '{question}', k={k}")
    settings = get_settings()
    
    logger.info("Setting up embeddings and vector store")
    embeddings = get_embeddings(settings)
    store = QdrantStore(settings, embeddings)
    retriever = store.as_retriever(collection_name=channel, k=k)

    logger.info("Setting up LLM")
    llm = get_llm(settings)

    logger.info("Building RAG chain")
    chain = (
        {"context": retriever | _format_docs, "question": RunnablePassthrough()}
        | RAG_PROMPT
        | llm
        | StrOutputParser()
    )

    logger.info("Invoking RAG chain to generate answer")
    answer = chain.invoke(question)
    logger.info(f"Generated answer: {answer[:100]}...")

    # also return top documents for transparency
    logger.info("Retrieving source documents")
    docs = retriever.get_relevant_documents(question)
    sources = [
        {"text": d.page_content, "metadata": d.metadata}
        for d in docs
    ]
    logger.info(f"Retrieved {len(sources)} source documents")
    return {"answer": answer, "sources": sources}
