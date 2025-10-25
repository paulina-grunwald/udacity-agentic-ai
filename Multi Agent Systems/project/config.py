import os
from dotenv import load_dotenv
from smolagents import LiteLLMModel

load_dotenv()

model = LiteLLMModel(model_id="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))
