import os
import re
import random
import requests
import google.generativeai as genai

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = "7290766676:AAE2D06PTzIqrG5u_jofvAIDjbhTPIRNbds"
GROUP_CHAT_ID = "-4596383816"

# Gemini AI Configuration
GEMINI_API_KEY = "AIzaSyDgPYwA_byvjxFLY5977G_ibIe7IWN1LAs"

# Configure Gemini AI
genai.configure(api_key=GEMINI_API_KEY)

# Gemini Model Configuration
generation_config = {
    "temperature": 0.7,
    "top_p": 0.85,
    "top_k": 40,
    "max_output_tokens": 8192,
}

# List of general greetings
GENERAL_GREETINGS = [
    "hi", "hello", "hey", "hi there", "good morning", "good afternoon", 
    "good evening", "greetings", "howdy", "sup", "what's up"
]

# List of gratitude phrases
GRATITUDE_PHRASES = [
    "thank you", "thanks", "thank u", "thankyou", 
    "appreciate it", "thx", "ty", "much appreciated"
]

# Greeting Responses
GREETING_RESPONSES = [
    "Hello! How are you today?", 
    "Hi there! What can I help you with?", 
    "Hey! Nice to see you.",
    "Greetings! How are you doing?",
    "Good to see you! How can I assist you today?"
]

# Gratitude Responses
GRATITUDE_RESPONSES = [
    "You're welcome! Happy to help.",
    "Glad I could assist you.",
    "No problem at all!",
    "Always here to help with Go programming questions.",
    "Happy to be of service!"
]

# System Prompt to constrain AI to Go Language topics
GOLANG_SYSTEM_PROMPT = """
You are a specialized Go (Golang) programming assistant. 
Your primary focus is on Go programming language topics:
- Language syntax and features
- Standard library
- Concurrency and goroutines
- Package management
- Best practices
- Code examples
- Go development tools

Provide clear, plain text responses without:
- Markdown formatting
- Code block markers
- Header symbols
- Bold or italic text
- Any special text annotations

For non-Go programming questions, respond with:
"Sorry, I can only provide detailed answers about the Go programming language. 
Please ask a Go-related question about syntax, libraries, concurrency, or development."
"""

# Initialize Gemini Model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config
)

def clean_response(text):
    """
    Remove markdown, code block markers, and other formatting
    """
    # Remove markdown formatting
    text = re.sub(r'[*_#`\[\]()]', '', text)
    
    # Remove code block markers
    text = text.replace('```', '')
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text

def is_general_greeting(text):
    """
    Check if the text is a general greeting
    """
    # Convert to lowercase and strip
    cleaned_text = text.lower().strip()
    
    # Check if the cleaned text is in general greetings
    return any(greeting in cleaned_text for greeting in GENERAL_GREETINGS)

def is_gratitude_phrase(text):
    """
    Check if the text is a gratitude phrase
    """
    # Convert to lowercase and strip
    cleaned_text = text.lower().strip()
    
    # Check if the cleaned text is in gratitude phrases
    return any(phrase in cleaned_text for phrase in GRATITUDE_PHRASES)

def send_telegram_message(chat_id, text):
    """
    Send a message to a Telegram chat
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    # Clean the response text
    cleaned_text = clean_response(text)
    
    response = requests.post(url, data={
        "chat_id": chat_id,
        "text": cleaned_text
    })
    
    if response.status_code != 200:
        print(f"Failed to send message: {response.json()}")
    return response

def handle_telegram_update(update):
    """
    Handle incoming Telegram updates
    """
    # Check if the message contains a text
    if 'message' in update and 'text' in update['message']:
        message = update['message']
        chat_id = message['chat']['id']
        text = message['text']
        
        # Check if the bot is tagged
        if f"@{bot_username}" in text:
            # Remove the bot tag from the message
            query = text.replace(f"@{bot_username}", "").strip()
            
            try:
                # Handle general greetings
                if is_general_greeting(query):
                    # Respond with a random greeting
                    response_text = random.choice(GREETING_RESPONSES)
                    send_telegram_message(chat_id, response_text)
                    return
                
                # Handle gratitude phrases
                if is_gratitude_phrase(query):
                    # Respond with a random gratitude response
                    response_text = random.choice(GRATITUDE_RESPONSES)
                    send_telegram_message(chat_id, response_text)
                    return
                
                # Start a new chat session for each query
                chat_session = model.start_chat(
                    history=[
                        {
                            'role': 'user',
                            'parts': [GOLANG_SYSTEM_PROMPT]
                        },
                        {
                            'role': 'model',
                            'parts': ["I understand. I will focus on Go programming language topics."]
                        }
                    ]
                )
                
                # Generate response using Gemini AI
                ai_response = chat_session.send_message(query)
                
                # Send the AI-generated response back to Telegram
                send_telegram_message(chat_id, ai_response.text)
            
            except Exception as e:
                error_message = f"An error occurred: {str(e)}"
                send_telegram_message(chat_id, error_message)

def start_bot():
    """
    Start the Telegram bot and listen for updates
    """
    # Get bot information
    global bot_username
    bot_info_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
    bot_info_response = requests.get(bot_info_url)
    
    if bot_info_response.status_code == 200:
        bot_username = bot_info_response.json()['result']['username']
    else:
        print("Failed to get bot information")
        return
    
    # Set up webhook or long polling
    offset = 0
    while True:
        try:
            # Get updates
            get_updates_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
            response = requests.get(get_updates_url, params={
                'offset': offset,
                'timeout': 30
            })
            
            if response.status_code == 200:
                updates = response.json().get('result', [])
                
                for update in updates:
                    # Process each update
                    handle_telegram_update(update)
                    
                    # Update offset to acknowledge processed updates
                    if updates:
                        offset = updates[-1]['update_id'] + 1
            
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    start_bot()