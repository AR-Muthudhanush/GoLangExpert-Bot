import os
import google.generativeai as genai

# Use environment variable for API key (recommended)
genai.configure(api_key="AIzaSyDgPYwA_byvjxFLY5977G_ibIe7IWN1LAs")

# Correct generation config
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
)

chat_session = model.start_chat(
  history=[]
)

response = chat_session.send_message("intro to GoLang")

print(response.text)