import re
from datetime import datetime
from typing import Dict, List

from langchain_core.documents import Document


def _strip_slack_formatting(text: str) -> str:
    # Remove user and channel mentions <@U123>, <#C123|name>, links <http://|text>
    text = re.sub(r"<@[A-Z0-9]+>", "", text)
    text = re.sub(r"<#([A-Z0-9]+)\|[^>]+>", r"#\1", text)
    text = re.sub(r"<([^>|]+)\|[^>]+>", r"\1", text)
    text = re.sub(r"<([^>]+)>", r"\1", text)
    # Collapse multiple spaces and trim
    text = re.sub(r"\s+", " ", text).strip()
    return text


def messages_to_documents(channel: str, messages: List[Dict]) -> List[Document]:
    docs: List[Document] = []
    for m in messages:
        text = m.get("text", "") or ""
        cleaned = _strip_slack_formatting(text)
        if not cleaned:
            continue
        ts = m.get("ts") or m.get("thread_ts") or ""
        dt: str = ""
        try:
            dt = datetime.fromtimestamp(float(ts)).isoformat()
        except Exception:
            dt = ""
        user = m.get("user") or m.get("username") or ""
        metadata = {
            "channel": channel,
            "ts": ts,
            "datetime": dt,
            "user": user,
        }
        docs.append(Document(page_content=cleaned, metadata=metadata))
    return docs
