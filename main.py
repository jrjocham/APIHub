import os
import requests
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

# Import our custom modules
from credentials import creds
from core import logger, handle_api_errors

# Initialize the Flask application
app = Flask(__name__)

# Initialize the Twilio client
client = Client(creds.twilio_account_sid, creds.twilio_auth_token)

# Map prefixes to Nomi IDs
NOMI_MAP = {
    "W:": creds.winston_id,
    "G:": creds.gates_id,
    "L:": creds.lexia_id
}

@app.route("/")
def health_check():
    """A simple health check endpoint."""
    return "API Hub is running!"

@app.route("/whatsapp", methods=['POST'])
@handle_api_errors
def whatsapp_webhook():
    # Get the incoming message
    incoming_message = request.values.get('Body', '').strip()
    from_number = request.values.get('From', '')

    logger.info(f"Received message from {from_number}: {incoming_message}")
    
    # Initialize Twilio MessagingResponse
    resp = MessagingResponse()

    # Check for the routing prefix
    prefix = incoming_message[:2]
    message_content = incoming_message[2:].strip()
    
    if prefix in NOMI_MAP:
        nomi_id = NOMI_MAP[prefix]
        
        # Send the message to the specified Nomi
        logger.info(f"Routing message to Nomi ID: {nomi_id}")
        nomi_response = send_to_nomi(nomi_id, message_content)
        
        # Send the Nomi's response back via Twilio
        resp.message(nomi_response)
        
    else:
        # If no valid prefix is found, send an error message
        logger.warning(f"Invalid prefix or no prefix found in message: '{incoming_message}'")
        resp.message("Please start your message with a valid prefix: W:, G:, or L: to talk to a Nomi.")

    return str(resp)

@handle_api_errors
def send_to_nomi(nomi_id: str, message: str) -> str:
    """
    Sends a message to the Nomi.ai API and returns the response.
    
    Args:
        nomi_id: The UUID of the Nomi to send the message to.
        message: The content of the message.
        
    Returns:
        The text response from the Nomi.
    """
    logger.info(f"Sending message to Nomi {nomi_id}...")

    api_url = f"https://api.nomi.ai/v1/nomis/{nomi_id}/message"
    headers = {
        "Authorization": f"Bearer {creds.nomi_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "message": message
    }

    response = requests.post(api_url, headers=headers, json=data)
    response.raise_for_status()
    
    response_data = response.json()
    
    nomi_message = response_data.get('message', 'No response from Nomi.')
    
    logger.info(f"Received response from Nomi {nomi_id}: {nomi_message}")
    
    return nomi_message

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)