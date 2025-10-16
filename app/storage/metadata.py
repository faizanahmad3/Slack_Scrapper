import json
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class IngestionMetadata:
    """Tracks ingestion metadata like last processed timestamp per channel."""
    
    def __init__(self, metadata_file: str = "ingestion_metadata.json"):
        self.metadata_file = Path(metadata_file)
        self.data: Dict[str, Dict] = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Dict]:
        """Load metadata from file."""
        if not self.metadata_file.exists():
            logger.info(f"Metadata file {self.metadata_file} doesn't exist, starting fresh")
            return {}
        
        try:
            with open(self.metadata_file, 'r') as f:
                data = json.load(f)
                logger.info(f"Loaded metadata for {len(data)} channels")
                return data
        except Exception as e:
            logger.error(f"Error loading metadata file: {e}")
            return {}
    
    def _save_metadata(self) -> None:
        """Save metadata to file."""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.data, f, indent=2)
                logger.debug(f"Saved metadata to {self.metadata_file}")
        except Exception as e:
            logger.error(f"Error saving metadata file: {e}")
    
    def get_last_timestamp(self, channel: str) -> Optional[str]:
        """Get the last processed message timestamp for a channel."""
        channel_data = self.data.get(channel, {})
        last_ts = channel_data.get("last_timestamp")
        if last_ts:
            logger.info(f"Last processed timestamp for channel '{channel}': {last_ts}")
        else:
            logger.info(f"No previous ingestion found for channel '{channel}'")
        return last_ts
    
    def update_last_timestamp(self, channel: str, timestamp: str, message_count: int) -> None:
        """Update the last processed timestamp for a channel."""
        if channel not in self.data:
            self.data[channel] = {}
        
        self.data[channel]["last_timestamp"] = timestamp
        self.data[channel]["total_messages"] = self.data[channel].get("total_messages", 0) + message_count
        self.data[channel]["last_updated"] = str(int(float(timestamp)))
        
        logger.info(f"Updated metadata for channel '{channel}': last_ts={timestamp}, new_messages={message_count}")
        self._save_metadata()
    
    def get_channel_stats(self, channel: str) -> Dict:
        """Get ingestion statistics for a channel."""
        return self.data.get(channel, {})
