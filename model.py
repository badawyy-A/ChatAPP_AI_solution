import os
import time
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

class GeminiLangChainClient:
    def __init__(self, model_name="llama3.1:8b", temperature=0.7):


        self.model_name = model_name
        self.temperature = temperature

    def _init_model(self):
        """Initialize a LangChain Gemini chat model with the given API key."""
        return ChatOllama(
            model=self.model_name,
            temperature=self.temperature,
            convert_system_message_to_human=True  # Helps ensure consistent message formats
        )

    def get_report(self, input_prompt, max_retries=3):
        """
        Attempts to generate a report using Gemini via LangChain,
        rotating across API keys if needed.

        Args:
            input_prompt (str): The prompt text to send to the model.
            max_retries (int): Number of retries per key before switching.

        Returns:
            str: The model-generated report or error message.
        """
        messages = [
            SystemMessage(content="You are a helpful assistant that writes detailed reports."),
            HumanMessage(content=input_prompt)
        ]

        
        model = self._init_model()

            
        response = model.invoke(messages)
        return response.content
           


