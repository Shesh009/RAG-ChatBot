import streamlit as st
import logging

logger = logging.getLogger(__name__)

class UIRenderer:
    def display_chat(self, chat_history, urls=None):
        try:
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
        except Exception as e:
            logger.error(f"Error rendering chat UI: {e}")
            st.markdown("An error occurred while rendering the chat interface.")
