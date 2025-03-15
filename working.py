import os
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
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
}

# Initialize Gemini Model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# Start a chat session
chat_session = model.start_chat(history=[])

def send_telegram_message(chat_id, text):
    """
    Send a message to a Telegram chat
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    response = requests.post(url, data={
        "chat_id": chat_id,
        "text": text
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