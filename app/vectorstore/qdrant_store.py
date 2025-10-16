from typing import Optional

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_community.vectorstores import Qdrant
from langchain_core.embeddings import Embeddings

from app.config import Settings


class QdrantStore:
    def __init__(self, settings: Settings, embeddings: Embeddings) -> None:
        self.settings = settings
        self.embeddings = embeddings
        self.client = QdrantClient(url=settings.qdrant_url, port=settings.qdrant_port)

    def ensure_collection(self, collection_name: str, vector_size: Optional[int] = None) -> None:
        exists = self.client.collection_exists(collection_name=collection_name)
        if not exists:
            if vector_size is None:
                # best effort probe: many OpenAI embedding sizes are known, but
                # we can lazily compute by embedding a trivial string.
                vector_size = len(self.embeddings.embed_query("hello"))
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )

    def as_vectorstore(self, collection_name: str) -> Qdrant:
        self.ensure_collection(collection_name)
        return Qdrant(
            client=self.client,
            collection_name=collection_name,
            embeddings=self.embeddings,
        )

    def as_retriever(self, collection_name: str, k: int = 5):
        vs = self.as_vectorstore(collection_name)
        return vs.as_retriever(search_kwargs={"k": k})
