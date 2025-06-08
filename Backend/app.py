from flask import Flask, request, jsonify
from chat_service import ChatService
from logging_config import setup_logging
import logging

app = Flask(__name__)
chat_service = ChatService()

setup_logging()
logger = logging.getLogger(__name__)

@app.route("/query", methods=["POST"])
def query_endpoint():
    try:
        data = request.get_json()
        query = data.get("query", "").strip()
        session_id = data.get("session_id", "default")
        logger.info(f"Incoming query: '{query}' | Session: {session_id}")

        if not query:
            logger.warning("Empty query received.")
            return jsonify({"answer": "No query provided."}), 400
        result = chat_service.handle_user_query(query, session_id)
        return jsonify(result), 200
    except Exception as e:
        logger.exception("Unhandled exception in /query endpoint.")
        return jsonify({"answer": "An internal error occurred."}), 500

if __name__ == "__main__":
    logger.info("Starting Flask app on port 5001")
    app.run(host="0.0.0.0", port=5001, debug=True)