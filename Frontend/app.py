import streamlit as st
import logging
from session_manager import SessionManager
from backend_client import BackendClient
from ui_renderer import UIRenderer
from logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

st.set_page_config(page_title="LLM-based RAG Chat")
st.title("LLM-based RAG Chatbot")

# Initialize session and components
session_manager = SessionManager()
backend_client = BackendClient()
ui_renderer = UIRenderer()

query = st.chat_input("Ask a question...")

if query:
    try:
        logger.info(f"[Session {session_manager.session_id}] User asked: {query}")
        session_manager.add_user_message(query)

        try:
            response = backend_client.send_query(query, session_manager.session_id)
            logger.info(f"[Session {session_manager.session_id}] Assistant response: {response['answer'][:80]}...")
            session_manager.add_assistant_message(response["answer"])

            ui_renderer.display_chat(session_manager.chat_history, response.get("urls", []))
        except Exception as e:
            logger.error(f"Error while getting response from backend: {e}")
            session_manager.add_assistant_message("Sorry, I couldn't process your request at the moment.")
            ui_renderer.display_chat(session_manager.chat_history)

    except Exception as e:
        logger.error(f"Error processing user query: {e}")
        session_manager.add_assistant_message("Sorry, there was an issue with your request.")
        ui_renderer.display_chat(session_manager.chat_history)
else:
    try:
        ui_renderer.display_chat(session_manager.chat_history)
    except Exception as e:
        logger.error(f"Error rendering chat history: {e}")
        st.markdown("An error occurred while loading the chat history.")
