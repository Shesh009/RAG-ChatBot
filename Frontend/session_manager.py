import streamlit as st
import uuid
import logging

logger = logging.getLogger(__name__)

class SessionManager:
    def __init__(self):
        if "session_id" not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
            logger.info(f"New session started: {st.session_state.session_id}")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

    @property
    def session_id(self):
        return st.session_state.session_id

    @property
    def chat_history(self):
        return st.session_state.chat_history

    def add_user_message(self, message):
        logger.info(f"[Session {self.session_id}] User message added")
        st.session_state.chat_history.append({"role": "user", "content": message})

    def add_assistant_message(self, message):
        logger.info(f"[Session {self.session_id}] Assistant message added")
        st.session_state.chat_history.append({"role": "assistant", "content": message})
