import requests
import logging

logger = logging.getLogger(__name__)

class BackendClient:
    def __init__(self):
        self.backend_urls = [
            "http://flask_backend:5001/query",
            "http://localhost:5001/query"
        ]

    def send_query(self, query, session_id):
        logger.info(f"Sending query for session {session_id} to backend")
        for url in self.backend_urls:
            try:
                response = requests.post(
                    url,
                    json={"query": query, "session_id": session_id},
                    timeout=30
                )
                if response.status_code == 200:
                    logger.info(f"Successful response from backend at {url}")
                    return response.json()
                else:
                    logger.warning(f"Backend {url} responded with status {response.status_code}")
            except requests.exceptions.RequestException as e:
                logger.error(f"Error contacting backend {url}: {e}")
        
        logger.error("All backend attempts failed.")
        return {"answer": "The chatbot is currently offline or unreachable.", "urls": []}
