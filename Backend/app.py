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
        if not data:
            logger.warning("Invalid or missing JSON payload.")
            return jsonify({"answer": "Invalid JSON payload."}), 400
        
        query = data.get("query", "").strip()
        session_id = data.get("session_id", "default")
        logger.info(f"Incoming query: '{query}' | Session: {session_id}")

        if not query:
            logger.warning("Empty query received.")
            return jsonify({"answer": "No query provided."}), 400

        try:
            result = chat_service.handle_user_query(query, session_id)
            return jsonify(result), 200
        except Exception as e:
            logger.exception("Error in handling user query.")
            return jsonify({"answer": "An internal error occurred while processing the query."}), 500
    except Exception as e:
        logger.exception("Unhandled exception in /query endpoint.")
        return jsonify({"answer": "An internal error occurred."}), 500

if __name__ == "__main__":
    try:
        logger.info("Starting Flask app on port 5001")
        app.run(host="0.0.0.0", port=5001, debug=True)
    except Exception as e:
        logger.exception("Failed to start Flask app.")
