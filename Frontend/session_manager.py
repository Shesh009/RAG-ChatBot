import streamlit as st
import uuid
import logging

logger = logging.getLogger(__name__)

class SessionManager:
    def __init__(self):
        try:
            if "session_id" not in st.session_state:
                st.session_state.session_id = str(uuid.uuid4())
                logger.info(f"New session started: {st.session_state.session_id}")

            if "chat_history" not in st.session_state:
                st.session_state.chat_history = []
        except Exception as e:
            logger.error(f"Error initializing session: {e}")
            st.session_state.session_id = str(uuid.uuid4())  # Fallback to a new session ID
            st.session_state.chat_history = []
            logger.info(f"New session created due to error: {st.session_state.session_id}")

    @property
    def session_id(self):
        return st.session_state.session_id

    @property
    def chat_history(self):
        return st.session_state.chat_history

    def add_user_message(self, message):
        try:
            logger.info(f"[Session {self.session_id}] User message added")
            st.session_state.chat_history.append({"role": "user", "content": message})
        except Exception as e:
            logger.error(f"Error adding user message to session: {e}")

    def add_assistant_message(self, message):
        try:
            logger.info(f"[Session {self.session_id}] Assistant message added")
            st.session_state.chat_history.append({"role": "assistant", "content": message})
        except Exception as e:
            logger.error(f"Error adding assistant message to session: {e}")
