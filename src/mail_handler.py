import os
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from src.config import config
from src.utils import Utils

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

class EmailManager:
    """
    Handles email-related operations using Gmail API.
    """
    def __init__(self, creds):
        self.creds = creds
        self.service = build("gmail", "v1", credentials=creds)

    def get_unread_emails_ids(self):
        """
        Retrieve unread emails from the inbox.
        Returns a list of message IDs.
        """
        try:
            results = self.service.users().messages().list(userId="me", labelIds=["INBOX", "UNREAD"]).execute()
            return results.get("messages", [])
        except HttpError as error:
            print(f"An HTTP error occurred while getting unread emails: {error}")
            return []

    def get_email_details(self, message_id):
        """
        Retrieve details (sender, subject, etc.) of a specific email.
        """
        try:
            message = self.service.users().messages().get(userId="me", id=message_id).execute()
            headers = message["payload"]["headers"]
            details = {
                "sender": next((header["value"] for header in headers if header["name"] == "From"), None),
                "subject": next((header["value"] for header in headers if header["name"] == "Subject"), None),
                "labels": message.get("labelIds", []),
            }
            return details
        except HttpError as error:
            print(f"An HTTP error occurred while getting email details: {error}")
            return {}

    def is_promo_email(self, message_id):
        """
        Check if an email is promotional based on sender, subject, or domain.
        """
        try:
            details = self.get_email_details(message_id)
            sender = details.get("sender", "")
            subject = details.get("subject", "")
            labels = details.get("labels", [])

            promotional_senders = Utils.read_file(config.PROMOTIONAL_SENDERS_FILE)
            promotional_subjects = Utils.read_file(config.PROMOTIONAL_SUBJECTS_FILE)
            promotional_domains = Utils.read_file(config.PROMOTIONAL_DOMAINS_FILE)

            domain = sender.split("@")[-1].split(">")[0] if sender else ""

            if any(keyword.lower() in sender.lower() for keyword in promotional_senders):
                return True
            if any(keyword.lower() in subject.lower() for keyword in promotional_subjects):
                return True
            if any(keyword.lower() in domain.lower() for keyword in promotional_domains):
                return True
            if "CATEGORY_PROMOTIONS" in labels:
                return True

            return False
        except Exception as e:
            print(f"An error occurred while checking for promotion email: {e}")
            return False

    def apply_label(self, message_id, label_name=None):
        """
        Apply a label to a specific email.
        If the label doesn't exist, it will be created.

        Args:
            message_id (str): The ID of the email to label.
            label_name (str): The name of the label to apply. If None is given, uses the default target folder.
        
        Returns:
            bool: True if the label was applied successfully, False otherwise.
        """
        if label_name is None:
            label_name = config.TARGET_FOLDER
            
        try:
            label_manager = LabelManager(self.creds, label_name)
            label_id = label_manager.get_label_id()
            
            if label_id:
                self.service.users().messages().modify(
                    userId="me",
                    id=message_id,
                    body={"addLabelIds": [label_id]}
                ).execute()
                return True
            return False
        except HttpError as error:
            print(f"An HTTP error occurred while applying label: {error}")
            return False

class LabelManager:
    """
    Handles label-related operations using Gmail API.
    """
    def __init__(self, creds, label_name=None):
        self.label_name = label_name if label_name else config.TARGET_FOLDER
        self.service = build("gmail", "v1", credentials=creds)

    def get_label_id(self):
        """
        Retrieve the ID of a specific label.
        """
        try:
            results = self.service.users().labels().list(userId="me").execute()
            labels = results.get("labels", [])
            for label in labels:
                if label["name"] == self.label_name:
                    return label["id"]
                    
            # If label doesn't exist, create it
            return self.create_label()
        except HttpError as error:
            print(f"An HTTP error occurred while getting label ID: {error}")
            return None
            
    def create_label(self):
        """
        Create a new label if it doesn't exist.
        """
        try:
            label = self.service.users().labels().create(
                userId="me",
                body={
                    "name": self.label_name,
                    "labelListVisibility": "labelShow",
                    "messageListVisibility": "show"
                }
            ).execute()
            print(f"Label '{self.label_name}' created successfully.")
            return label["id"]
        except HttpError as error:
            print(f"An HTTP error occurred while creating label: {error}")
            return None

def test_gmail_api(creds):
    """
    Test the connection to the Gmail API.
    """
    try:
        service = build("gmail", "v1", credentials=creds)
        results = service.users().labels().list(userId="me").execute()
        labels = results.get("labels", [])
        
        if not labels:
            print("No labels found.")
        else:
            print("Connection to Gmail API successful.")
            print(f"Found {len(labels)} labels.")
        return True
    except HttpError as error:
        print(f"An HTTP error occurred: {error}")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False