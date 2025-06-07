from langchain.llms.base import LLM
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

class GeminiLLM(LLM):
    model_name: str = "gemini-2.0-flash"

    def _call(self, prompt: str, stop=None) -> str:
        response = genai.GenerativeModel(self.model_name).generate_content(prompt)
        return response.text.strip()

    @property
    def _identifying_params(self):
        return {"model_name": self.model_name}

    @property
    def _llm_type(self):
        return "gemini"