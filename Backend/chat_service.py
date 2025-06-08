from langchain.llms.base import LLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from collections import defaultdict
import os
import logging

from llm_wrapper import GeminiLLM
from qdrant_manager import QdrantManager
from search_scraper import SearchScraper

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
      self.llm = GeminiLLM()
      self.qdrant = QdrantManager()
      self.scraper = SearchScraper()
      self.memory_store = defaultdict(lambda: ConversationBufferMemory(memory_key="chat_history", return_messages=True))

      self.contextualize_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=["chat_history", "current_query"],
                template="Given the chat history and the latest question, rewrite the question so it is standalone and complete.\n\nChat History:\n{chat_history}\n\nLatest Question: {current_query}\n\nStandalone Question:"
            )
        )

      self.answer_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=["context", "question"],
                template="You are a helpful assistant. Use the context and question below to answer the user's question.\n\nContext:\n{context}\n\nQuestion: {question}\n\nAnswer:"
            )
        )
      
    def handle_user_query(self, user_query, session_id="default"):
        logger.info(f"Handling user query for session: {session_id}")
        memory = self.memory_store[session_id]

        try:
            history_msgs = memory.load_memory_variables({})["chat_history"]
            history_text = "\n".join([msg.content for msg in history_msgs if msg.type == "human"])

            standalone_question = self.contextualize_chain.run(
                chat_history=history_text, current_query=user_query)

            urls = self.scraper.search(standalone_question)
            context = self.scraper.scrape(urls)

            if not context:
                logger.warning("No useful context found.")
                return {"answer": "No useful documents found."}

            self.qdrant.add_texts(session_id, [user_query, context])
            similar_docs = self.qdrant.search_similar(standalone_question, session_id)
            combined_context = "\n\n".join(similar_docs) + "\n\n" + context

            answer = self.answer_chain.run(context=combined_context, question=standalone_question)
            memory.save_context({"input": user_query}, {"output": answer})

            logger.info("Query handled successfully.")
            return {"answer": answer, "urls": urls}
        except Exception as e:
            logger.exception("Failed to handle user query.")
            return {"answer": "An internal error occurred."}