import streamlit as st
import logging

logger = logging.getLogger(__name__)

class UIRenderer:
    def display_chat(self, chat_history, urls=None):
        logger.debug("Rendering chat history...")
        for msg in chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if urls:
            logger.info(f"Displaying {len(urls)} reference URLs")
            with st.chat_message("assistant"):
                st.markdown("### References:")
                for url in urls:
                    st.markdown(f"- [{url}]({url})")
