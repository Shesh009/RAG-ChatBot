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

backend_urls = [
    "http://llm_search_template_backend_1:5001/query",  
    "http://localhost:5001/query"                       
]

if query:
    st.session_state.chat_history.append({"role": "user", "content": query})

    res = None
    for url in backend_urls:
        try:
            res = requests.post(
                url,
                json={
                    "query": query,
                    "session_id": st.session_state.session_id
                },
                timeout=30
            )
            print(f"[DEBUG] Trying URL: {url}")
            print(f"[DEBUG] Status: {res.status_code}")
            print(f"[DEBUG] Body: {res.text}")
            if res.status_code == 200:
                break
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to connect to {url}: {e}")

    if res and res.status_code == 200:
        try:
            answer = res.json().get("answer", "No answer received.")
        except Exception as e:
            answer = f"Failed to parse JSON: {e}"
    else:
        answer = "The chatbot is currently offline or unreachable."

    st.session_state.chat_history.append({"role": "assistant", "content": answer})

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])