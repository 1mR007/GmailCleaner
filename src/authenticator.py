# src/authenticator.py

import os
import time

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError

class Authenticator:
    """
    Handles Gmail API authentication.
    """
    SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

    def __init__(self):
        self.creds = None

    def authenticate(self):
        """
        Authenticate the user and return credentials.
        """
        try:
            if os.path.exists("token.json"):
                self.creds = Credentials.from_authorized_user_file("token.json", self.SCOPES)
                if self.creds and self.creds.valid:
                    print("Token is valid, Gmail API can be accessed.")
                    return self.creds
                elif self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                    print("Token refreshed.")
                    return self.creds
            else:
                print("Token file not found. Starting authentication flow.")
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", self.SCOPES)
                self.creds = flow.run_local_server(port=0)
                with open("token.json", "w") as token_file:
                    token_file.write(self.creds.to_json())
                print("Token saved to token.json.")
                return self.creds
        except Exception as e:
            print(f"Authentication error: {e}")
            return None
        
    def test_gmail_api(self, service):
        """
        Test the connection to the Gmail API.
        """
        try:
            start = time.time()
            results = service.users().labels().list(userId="me").execute()
            labels = results.get("labels", [])
            end = time.time()
            
            if not labels:
                print("No labels found.")
            else:
                print("Connection to Gmail API successful.")
                print(f"Found {len(labels)} labels in {round(end - start, 2)}s.")
            return True
        except HttpError as error:
            print(f"An HTTP error occurred: {error}")
            return False
        except Exception as e:
            print(f"An error occurred: {e}")
            return False