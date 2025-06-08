from langchain.llms.base import LLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from collections import defaultdict
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
            try:
                history_msgs = memory.load_memory_variables({})["chat_history"]
                history_text = "\n".join([msg.content for msg in history_msgs if msg.type == "human"])
            except Exception as e:
                logger.error(f"Failed to load chat history for session {session_id}: {e}")
                raise ValueError("Unable to load chat history.")

            # Contextualize the query
            try:
                standalone_question = self.contextualize_chain.run(chat_history=history_text, current_query=user_query)
            except Exception as e:
                logger.error(f"Error while contextualizing query for session {session_id}: {e}")
                raise ValueError("Failed to contextualize the question.")

            # Perform search and scrape
            try:
                urls = self.scraper.search(standalone_question)
                context = self.scraper.scrape(urls)
            except Exception as e:
                logger.error(f"Error during scraping for session {session_id}: {e}")
                raise ValueError("Error retrieving search results.")

            if not context:
                logger.warning("No useful context found.")
                return {"answer": "No useful documents found."}

            # Add texts to Qdrant and search for similar documents
            try:
                self.qdrant.add_texts(session_id, [user_query, context])
                similar_docs = self.qdrant.search_similar(standalone_question, session_id)
            except Exception as e:
                logger.error(f"Error interacting with Qdrant for session {session_id}: {e}")
                raise ValueError("Failed to interact with the Qdrant database.")

            combined_context = "\n\n".join(similar_docs) + "\n\n" + context

            # Generate the answer
            try:
                answer = self.answer_chain.run(context=combined_context, question=standalone_question)
                memory.save_context({"input": user_query}, {"output": answer})
            except Exception as e:
                logger.error(f"Error generating answer for session {session_id}: {e}")
                raise ValueError("Failed to generate answer from the model.")

            logger.info(f"Query handled successfully for session {session_id}.")
            return {"answer": answer, "urls": urls}
        except Exception as e:
            logger.exception(f"Failed to handle user query for session {session_id}: {e}")
            return {"answer": "An internal error occurred."}
