from fastapi import FastAPI, HTTPException
import uvicorn
import os
import logging

# Setup logging first
from app.logging_config import setup_logging
setup_logging("INFO")

from app.api.schemas import QARequest, QAResponse, SourceDoc, ChannelStatsResponse
from app.config import get_settings
from app.pipelines.ingest import ingest_channel
from app.pipelines.qa import answer_question
from app.ingestion.slack_client import SlackIngestionClient
from app.storage.metadata import IngestionMetadata

logger = logging.getLogger(__name__)
app = FastAPI(title="Slack Channel Q&A", version="0.1.1")


@app.get("/health")
def health() -> dict:
    logger.info("Health check requested")
    return {"status": "ok"}


@app.get("/channels")
def list_channels(include_private: bool = True) -> dict:
    logger.info(f"Listing channels, include_private={include_private}")
    try:
        client = SlackIngestionClient(get_settings())
        names = client.list_channel_names(include_private=include_private)
        logger.info(f"Found {len(names)} channels: {names}")
        return {"channels": names}
    except Exception as e:
        logger.error(f"Error listing channels: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/qa", response_model=QAResponse)
def qa(request: QARequest) -> QAResponse:
    logger.info(f"QA request for channel '{request.channel}', query: '{request.query}', refresh: {request.refresh}")
    settings = get_settings()

    if request.refresh:
        try:
            logger.info(f"Starting ingestion for channel: {request.channel}, force_full_refresh: {request.force_full_refresh}")
            doc_count = ingest_channel(request.channel, force_full_refresh=request.force_full_refresh)
            logger.info(f"Ingested {doc_count} documents for channel: {request.channel}")
        except Exception as e:
            logger.error(f"Error during ingestion for channel '{request.channel}': {e}")
            raise HTTPException(status_code=400, detail=str(e))

    try:
        logger.info(f"Answering question for channel '{request.channel}' with top_k={request.top_k}")
        result = answer_question(request.channel, request.query, k=request.top_k)
        logger.info(f"Generated answer with {len(result.get('sources', []))} sources")
    except ValueError as e:
        logger.error(f"ValueError in QA for channel '{request.channel}': {e}")
        # Likely collection missing or channel not found
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in QA for channel '{request.channel}': {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return QAResponse(
        answer=result["answer"],
        sources=[SourceDoc(**s) for s in result["sources"]],
    )


@app.get("/channels/{channel}/stats", response_model=ChannelStatsResponse)
def get_channel_stats(channel: str) -> ChannelStatsResponse:
    logger.info(f"Getting stats for channel: {channel}")
    try:
        metadata = IngestionMetadata()
        stats = metadata.get_channel_stats(channel)
        logger.info(f"Channel '{channel}' stats: {stats}")
        return ChannelStatsResponse(
            channel=channel,
            last_timestamp=stats.get("last_timestamp"),
            total_messages=stats.get("total_messages", 0),
            last_updated=stats.get("last_updated")
        )
    except Exception as e:
        logger.error(f"Error getting stats for channel '{channel}': {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)