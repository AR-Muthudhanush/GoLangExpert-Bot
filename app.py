import requests

# Replace with your actual API key and group chat ID
API_KEY = "7290766676:AAE2D06PTzIqrG5u_jofvAIDjbhTPIRNbds"
GROUP_CHAT_ID = "-4596383816"  # Replace with your group chat ID
MESSAGE = "Hi ✌️😄"

# URL to send the message
URL = f"https://api.telegram.org/bot7290766676:AAE2D06PTzIqrG5u_jofvAIDjbhTPIRNbds/sendMessage"

# Sending the message
response = requests.post(URL, data={
    "chat_id": GROUP_CHAT_ID,
    "text": MESSAGE
})

if response.status_code == 200:
    print("Message sent successfully!")
else:
    print("Failed to send message:", response.json())
