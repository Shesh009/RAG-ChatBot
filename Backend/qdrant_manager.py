import time
import httpx
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from sentence_transformers import SentenceTransformer

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
                        return host
                except httpx.ConnectError:
                    time.sleep(delay)
        raise ConnectionError("Qdrant is not available.")

    def _wait_for_qdrant(self, port=6333, retries=10, delay=3):
        url = f"http://{self.host}:{port}/collections"
        for _ in range(retries):
            try:
                if httpx.get(url).status_code == 200:
                    return
            except httpx.ConnectError:
                time.sleep(delay)
        raise ConnectionError("Qdrant did not become available.")

    def _ensure_collection(self):
        try:
            self.client.get_collection(self.collection_name)
        except Exception:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )

    def add_texts(self, session_id, texts):
        embeddings = self.embedder.encode(texts)
        points = [{"id": i, "vector": emb, "payload": {"session_id": session_id, "text": text}}
                  for i, (text, emb) in enumerate(zip(texts, embeddings))]
        self.client.upsert(collection_name=self.collection_name, points=points)

    def search_similar(self, query, session_id, k=5):
        query_vector = self.embedder.encode([query])[0]
        results = self.client.search(collection_name=self.collection_name, query_vector=query_vector, limit=k)
        return [res.payload["text"] for res in results]