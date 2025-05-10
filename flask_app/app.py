from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os, requests, urllib.parse
from bs4 import BeautifulSoup
import google.generativeai as genai
from collections import defaultdict

# Setup
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')

app = Flask(__name__)
chat_history_store = defaultdict(list)

def update_chat_history(session_id, role, content):
    chat_history_store[session_id].append({"role": role, "content": content})

def get_chat_history(session_id):
    return chat_history_store[session_id]

def contextualize_query(session_id, current_query):
    history = get_chat_history(session_id)
    history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history if msg['role'] == "user"])

    prompt = (
        "Given the chat history and the latest question, rewrite the question so it is standalone and complete.\n\n"
        f"Chat History:\n{history_text}\n\n"
        f"Latest Question: {current_query}\n\n"
        "Standalone Question:"
    )
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"[ERROR] Gemini contextualize_query failed: {e}")
        return current_query 

def search_duckduckgo(query, max_results=5):
    print(f"[INFO] Searching DuckDuckGo for: {query}")
    search_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    links = []
    for a in soup.find_all('a', class_='result__a', href=True):
        raw_url = a['href']
        parsed = urllib.parse.urlparse(raw_url)
        actual_url = urllib.parse.parse_qs(parsed.query).get('uddg', [None])[0]
        if actual_url and not any(bad in actual_url for bad in ['youtube', 'twitter', 'facebook']):
            links.append(actual_url)
        if len(links) >= max_results:
            break
    print(f"[INFO] Found {len(links)} URLs")
    return links

def scrape_articles(urls):
    contents = []
    for url in urls:
        try:
            print(f"[SCRAPE] {url}")
            html = requests.get(url, timeout=5).text
            soup = BeautifulSoup(html, "html.parser")
            text = " ".join(h.get_text() for h in soup.find_all(['h1', 'h2', 'h3'])) + "\n" + \
                   " ".join(p.get_text() for p in soup.find_all('p'))
            contents.append(text.strip())
        except Exception as e:
            print(f"[ERROR] Failed scraping {url}: {e}")
    return "\n\n".join(contents)[:100000]

def answer_question(context, question, history):
    prompt = (
        "You are a helpful assistant. Use the context and question below to answer the user's question.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        "Generate the creative answer with above requirements"
    )
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"[ERROR] Gemini answer_question failed: {e}")
        return "I'm sorry, there was an error generating the answer."

@app.route("/query", methods=["POST"])
def handle_query():
    try:
        data = request.json
        user_query = data.get("query", "").strip()
        session_id = data.get("session_id", "default")

        print(f"[QUERY] Session: {session_id} | User: {user_query}")

        if not user_query:
            return jsonify({"answer": "No query provided."}), 400

        update_chat_history(session_id, "user", user_query)

        contextual_query = contextualize_query(session_id, user_query)
        urls = search_duckduckgo(contextual_query)
        context = scrape_articles(urls)

        if not context:
            return jsonify({"answer": "No useful documents found."}), 200

        answer = answer_question(context, contextual_query, get_chat_history(session_id))
        update_chat_history(session_id, "assistant", answer)

        print(f"[RESPONSE] {answer[:300]}...")
        return jsonify({"answer": answer}), 200

    except Exception as e:
        print(f"[ERROR] Unhandled exception: {e}")
        return jsonify({"answer": "An internal error occurred."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)