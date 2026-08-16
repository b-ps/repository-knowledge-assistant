
from openai import OpenAI
from dotenv import load_dotenv
import os


load_dotenv()


class LLM:

    def __init__(self, model: str = "llama-3.3-70b-versatile"):
        self.client = OpenAI(
            api_key = os.getenv("GROQ_API_KEY"),
            base_url = "https://api.groq.com/openai/v1"
        )
        self.model = model
    
    def generate(self, instructions: str, prompt: str) -> str:
        message = [
            {"role": "developer", "content": instructions},
            {"role": "user", "content": prompt}
        ]

        response = self.client.responses.create(
            model=self.model,
            input=message
        )

        return response.output_text