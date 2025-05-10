import streamlit as st
import requests
import uuid

st.set_page_config(page_title="LLM-based RAG Chat")
st.title("LLM-based RAG Chatbot")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

query = st.chat_input("Ask a question...")

if query:
    st.session_state.chat_history.append({"role": "user", "content": query})

    try:
        res = requests.post(
            "http://llm_search_template_backend_1:5001/query",
            json={
                "query": query,
                "session_id": st.session_state.session_id
            },
            timeout=30  # increased timeout
        )

        print(f"[DEBUG] Status: {res.status_code}")
        print(f"[DEBUG] Body: {res.text}")

        if res.status_code == 200:
            try:
                answer = res.json().get("answer", "No answer received.")
            except Exception as e:
                answer = f"Failed to parse JSON: {e}"
        else:
            answer = f"Error from server: {res.status_code}"

    except requests.exceptions.RequestException as e:
        answer = f"The chatbot is currently offline or unreachable.\n\nDetails: {e}"

    st.session_state.chat_history.append({"role": "assistant", "content": answer})

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])