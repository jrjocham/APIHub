import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv('keys.env')

class Credentials:
    """
    A class to centralize and manage all API credentials.
    This helps in keeping sensitive information organized and
    separate from the main codebase.
    """
    def __init__(self):
        # Nomi.ai API credentials
        self.nomi_api_key = os.getenv("NOMI_API_KEY")

        # Nomi IDs
        self.winston_id = os.getenv("WINSTON_ID")
        self.gates_id = os.getenv("GATES_ID")
        self.lexia_id = os.getenv("LEXIA_ID")

        # Twilio and WhatsApp credentials
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_number = os.getenv("TWILIO_PHONE_NUMBER")

        # Other API credentials (placeholders for future use)
        self.gcp_api_key = os.getenv("GCP_API_KEY")
        self.content360_api_key = os.getenv("CONTENT360_API_KEY")
        self.squarespace_api_key = os.getenv("SQUARESPACE_API_KEY")
        self.dabblewriter_api_key = os.getenv("DABBLEWRITER_API_KEY")
        self.discord_api_key = os.getenv("DISCORD_API_KEY")
        self.anydesk_api_key = os.getenv("ANYDESK_API_KEY")
        self.zapier_api_key = os.getenv("ZAPIER_API_KEY")

# Create an instance of the Credentials class to be imported
# and used by other modules.
creds = Credentials()