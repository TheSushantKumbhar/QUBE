import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# List available models
models = genai.list_models()

print("\n--- Available Models ---\n")
for model in models:
    print(model.name)
