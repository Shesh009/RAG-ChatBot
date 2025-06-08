import logging
import time
import httpx
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class QdrantManager:
    def __init__(self, collection_name="chat_history"):
        self.collection_name = collection_name
        self.host = self._get_available_host()
        self._wait_for_qdrant()
        self.client = QdrantClient(host=self.host, port=6333)
        self._ensure_collection()
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

    def _get_available_host(self, port=6333, retries=5, delay=2):
        hosts = ["localhost", "qdrant"]
        for host in hosts:
            url = f"http://{host}:{port}/collections"
            for _ in range(retries):
                try:
                    if httpx.get(url).status_code == 200:
                        logger.info(f"Qdrant available at {host}")
                        return host
                except httpx.ConnectError as e:
                    logger.warning(f"Failed to connect to Qdrant at {host}: {e}")
                    time.sleep(delay)
        raise ConnectionError("Qdrant is not available after multiple attempts.")

    def _wait_for_qdrant(self, port=6333, retries=10, delay=3):
        url = f"http://{self.host}:{port}/collections"
        for _ in range(retries):
            try:
                if httpx.get(url).status_code == 200:
                    logger.info("Qdrant became available.")
                    return
            except httpx.ConnectError as e:
                logger.warning(f"Failed to connect to Qdrant: {e}")
                time.sleep(delay)
        raise ConnectionError("Qdrant did not become available after retries.")

    def _ensure_collection(self):
        try:
            self.client.get_collection(self.collection_name)
            logger.info("Qdrant collection already exists.")
        except Exception as e:
            logger.info("Creating new Qdrant collection.")
            try:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
                )
            except Exception as e:
                logger.error(f"Failed to create Qdrant collection: {e}")
                raise ValueError("Failed to create or access Qdrant collection.")

    def add_texts(self, session_id, texts):
        try:
            logger.info(f"Adding texts to Qdrant for session: {session_id}")
            embeddings = self.embedder.encode(texts)
            points = [{"id": i, "vector": emb, "payload": {"session_id": session_id, "text": text}} for i, (text, emb) in enumerate(zip(texts, embeddings))]
            self.client.upsert(collection_name=self.collection_name, points=points)
        except Exception as e:
            logger.error(f"Error adding texts to Qdrant for session {session_id}: {e}")
            raise ValueError("Failed to add texts to Qdrant.")

    def search_similar(self, query, session_id, k=5):
        try:
            logger.info(f"Searching similar documents for session: {session_id}")
            query_vector = self.embedder.encode([query])[0]
            results = self.client.search(collection_name=self.collection_name, query_vector=query_vector, limit=k)
            return [res.payload["text"] for res in results]
        except Exception as e:
            logger.error(f"Error searching similar documents in Qdrant for session {session_id}: {e}")
            raise ValueError("Failed to search similar documents in Qdrant.")
