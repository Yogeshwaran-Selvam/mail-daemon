import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# This scope allows us to read and modify emails (like removing the INBOX label)
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def get_gmail_service():
    """Authenticates with the Gmail API and returns the service object."""
    creds = None
    
    # 1. Check if we already have a valid token saved from a previous login
    # In production, you would want to store this path in your .env file
    token_path = 'token.json'
    creds_path = 'credentials.json'

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
    # 2. If we don't have valid credentials, we need to log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Refresh the token if it just expired
            creds.refresh(Request())
        else:
            # Trigger the Google Login Pop-up
            if not os.path.exists(creds_path):
                raise FileNotFoundError(
                    "Missing credentials.json! Download it from Google Cloud Console."
                )
            
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
            
        # 3. Save the fresh token for the next time so we don't have to log in again
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    # 4. Build and return the API service
    try:
        service = build('gmail', 'v1', credentials=creds)
        return service
    except Exception as error:
        print(f'An error occurred connecting to Gmail API: {error}')
        return None

# Add this temporarily to the bottom of the file
if __name__ == '__main__':
    service = get_gmail_service()
    if service:
        print("Success! Token generated.")