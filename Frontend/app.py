import streamlit as st
from session_manager import SessionManager
from backend_client import BackendClient
from ui_renderer import UIRenderer

st.set_page_config(page_title="LLM-based RAG Chat")
st.title("LLM-based RAG Chatbot")

# Initialize session manager
session_manager = SessionManager()
query = st.chat_input("Ask a question...")

# Initialize backend client and UI renderer
backend_client = BackendClient()
ui_renderer = UIRenderer()

if query:
    session_manager.add_user_message(query)
    response = backend_client.send_query(query, session_manager.session_id)
    session_manager.add_assistant_message(response["answer"])
    ui_renderer.display_chat(session_manager.chat_history, response.get("urls", []))
else:
    ui_renderer.display_chat(session_manager.chat_history)
