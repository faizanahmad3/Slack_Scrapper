import logging
from typing import List, Optional

from langchain_core.documents import Document

from app.config import get_settings
from app.ingestion.slack_client import SlackIngestionClient
from app.processing.clean import messages_to_documents
from app.providers.registry import get_embeddings
from app.storage.metadata import IngestionMetadata
from app.vectorstore.qdrant_store import QdrantStore

logger = logging.getLogger(__name__)


def ingest_channel(channel: str, force_full_refresh: bool = False) -> int:
    logger.info(f"Starting ingestion pipeline for channel: {channel}, force_full_refresh: {force_full_refresh}")
    settings = get_settings()
    slack = SlackIngestionClient(settings)
    metadata = IngestionMetadata()
    
    channel_id = slack.get_channel_id(channel)
    if not channel_id:
        logger.error(f"Channel '{channel}' not found")
        raise ValueError(f"Channel not found: {channel}")

    # Determine oldest timestamp for incremental updates
    oldest_timestamp: Optional[str] = None
    if not force_full_refresh:
        last_timestamp = metadata.get_last_timestamp(channel)
        if last_timestamp:
            # Use the exact last timestamp - Slack API will return messages AFTER this timestamp
            oldest_timestamp = last_timestamp
            stats = metadata.get_channel_stats(channel)
            logger.info(f"========== INCREMENTAL UPDATE MODE ==========")
            logger.info(f"  Last processed timestamp: {oldest_timestamp}")
            logger.info(f"  Total messages processed so far: {stats.get('total_messages', 0)}")
            logger.info(f"  Fetching only NEW messages after this timestamp...")
            logger.info(f"=============================================")
        else:
            logger.info("========== FIRST-TIME FULL INGESTION ==========")
            logger.info("  No previous ingestion found")
            logger.info("  Fetching ALL messages from channel history...")
            logger.info("===============================================")
    else:
        logger.info("========== FORCE FULL REFRESH MODE ==========")
        logger.info("  Re-ingesting ENTIRE channel (ignoring previous state)")
        logger.info("=============================================")

    logger.info(f"Fetching messages for channel '{channel}' (ID: {channel_id})")
    messages = slack.fetch_messages(channel_id, oldest=oldest_timestamp)
    logger.info(f"Fetched {len(messages)} raw messages from Slack API")
    
    # Filter out messages we've already processed (same timestamp as last processed)
    if oldest_timestamp and messages:
        original_count = len(messages)
        messages = [msg for msg in messages if msg.get("ts", "0") > oldest_timestamp]
        filtered_count = len(messages)
        logger.info(f"Filtered messages: {original_count} -> {filtered_count} (removed {original_count - filtered_count} already processed)")
    
    # Log details of each message being ingested
    if messages:
        logger.info(f"========== INGESTING {len(messages)} NEW MESSAGES ==========")
        for idx, msg in enumerate(messages, 1):
            ts = msg.get("ts", "unknown")
            text = msg.get("text", "")
            text_preview = text[:100] + "..." if len(text) > 100 else text
            user = msg.get("user", "unknown")
            logger.info(f"  [{idx}] ts={ts}, user={user}, text='{text_preview}'")
        logger.info(f"========== END OF NEW MESSAGES ==========")
    
    logger.info(f"Processing {len(messages)} new messages into documents")
    
    if not messages:
        logger.info(f"No new messages found for channel '{channel}'")
        return 0
    
    docs: List[Document] = messages_to_documents(channel, messages)
    logger.info(f"Created {len(docs)} documents from messages")

    if not docs:
        logger.warning(f"No documents created for channel '{channel}'")
        return 0

    logger.info(f"Setting up embeddings and vector store for channel '{channel}'")
    embeddings = get_embeddings(settings)
    store = QdrantStore(settings, embeddings)
    vectorstore = store.as_vectorstore(collection_name=channel)

    logger.info(f"Adding {len(docs)} new documents to vector store")
    vectorstore.add_documents(docs)
    
    # Update metadata with the latest message timestamp
    latest_timestamp = max(msg.get("ts", "0") for msg in messages)
    metadata.update_last_timestamp(channel, latest_timestamp, len(messages))
    
    logger.info(f"Successfully ingested {len(docs)} documents for channel '{channel}'")
    return len(docs)
