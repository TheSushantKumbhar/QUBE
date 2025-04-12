import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Use a valid model from the list
model = genai.GenerativeModel("models/gemini-1.5-pro")  # or try "models/gemini-1.5-flash"

response = model.generate_content("Give me one quiz question on Newton's Laws of Motion.")

print(response.text)
