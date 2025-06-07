from flask import Flask, request, jsonify
from chat_service import ChatService

app = Flask(__name__)
chat_service = ChatService()

@app.route("/query", methods=["POST"])
def query_endpoint():
    try:
        data = request.get_json()
        query = data.get("query", "").strip()
        session_id = data.get("session_id", "default")
        if not query:
            return jsonify({"answer": "No query provided."}), 400
        result = chat_service.handle_user_query(query, session_id)
        return jsonify(result), 200
    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({"answer": "An internal error occurred."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)