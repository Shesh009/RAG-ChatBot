import streamlit as st

class UIRenderer:
    def display_chat(self, chat_history, urls=None):
        for msg in chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if urls:
            with st.chat_message("assistant"):
                st.markdown("### References:")
                for url in urls:
                    st.markdown(f"- [{url}]({url})")
