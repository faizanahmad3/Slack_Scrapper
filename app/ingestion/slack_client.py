import time
import logging
from typing import Dict, Iterable, List, Optional

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from app.config import Settings

logger = logging.getLogger(__name__)


class SlackIngestionClient:
    def __init__(self, settings: Settings) -> None:
        logger.info("Initializing SlackIngestionClient")
        if not settings.slack_bot_token:
            logger.error("SLACK_BOT_TOKEN is missing")
            raise ValueError("SLACK_BOT_TOKEN is required for Slack ingestion")
        self.client = WebClient(token=settings.slack_bot_token)
        self.max_messages = settings.max_messages_per_channel
        logger.info(f"SlackIngestionClient initialized with max_messages: {self.max_messages}")

    def get_channel_id(self, channel_name: str) -> Optional[str]:
        logger.info(f"Looking up channel ID for: {channel_name}")
        cursor: Optional[str] = None
        while True:
            response = self.client.conversations_list(limit=1000, cursor=cursor)
            for ch in response["channels"]:
                if ch.get("name") == channel_name:
                    channel_id = ch.get("id")
                    logger.info(f"Found channel ID '{channel_id}' for channel '{channel_name}'")
                    return channel_id
            cursor = response.get("response_metadata", {}).get("next_cursor") or None
            if not cursor:
                break
        logger.warning(f"Channel '{channel_name}' not found")
        return None

    def list_channels(self, include_private: bool = True) -> List[Dict]:
        logger.info(f"Listing channels, include_private={include_private}")
        channels: List[Dict] = []
        cursor: Optional[str] = None
        types = "public_channel,private_channel" if include_private else "public_channel"
        while True:
            response = self.client.conversations_list(limit=1000, cursor=cursor, types=types)
            batch = response.get("channels", [])
            channels.extend(batch)
            logger.debug(f"Retrieved {len(batch)} channels in this batch")
            cursor = response.get("response_metadata", {}).get("next_cursor") or None
            if not cursor:
                break
        logger.info(f"Total channels found: {len(channels)}")
        return channels

    def list_channel_names(self, include_private: bool = True) -> List[str]:
        channels = self.list_channels(include_private=include_private)
        names = [c.get("name", "") for c in channels if c.get("name")]
        logger.info(f"Channel names: {names}")
        return names

    def fetch_messages(self, channel_id: str, oldest: Optional[str] = None) -> List[Dict]:
        logger.info(f"Fetching messages for channel ID: {channel_id}, oldest: {oldest}")
        messages: List[Dict] = []
        cursor: Optional[str] = None
        remaining = self.max_messages if self.max_messages else float("inf")
        logger.info(f"Max messages to fetch: {remaining}")
        
        while remaining > 0:
            try:
                limit = 200 if remaining == float("inf") else min(200, int(remaining))
                logger.debug(f"Fetching batch with limit: {limit}, cursor: {cursor}")
                
                # Build request parameters
                params = {"channel": channel_id, "limit": limit}
                if cursor:
                    params["cursor"] = cursor
                if oldest:
                    params["oldest"] = oldest
                
                response = self.client.conversations_history(**params)
                batch = response.get("messages", [])
                messages.extend(batch)
                remaining -= len(batch)
                logger.debug(f"Fetched {len(batch)} messages, {len(messages)} total, {remaining} remaining")
                cursor = response.get("response_metadata", {}).get("next_cursor") or None
                if not cursor or not batch:
                    break
            except SlackApiError as e:
                if e.response["error"] == "ratelimited":
                    retry_after = int(e.response.headers.get("Retry-After", 5))
                    logger.warning(f"Rate limited, sleeping for {retry_after} seconds")
                    time.sleep(retry_after)
                    continue
                logger.error(f"Slack API error: {e}")
                raise
        # oldest first
        messages.reverse()
        logger.info(f"Fetched total of {len(messages)} messages for channel {channel_id}")
        return messages
