import os.path
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import config
import utils

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

def start_gmail_api():
  """
  Start the Gmail API by checking for existing credentials and refreshing them if necessary.
  If no credentials are found, it prompts the user to log in and saves the credentials (token.json) for future use.

  Returns:
  creds (Credentials): The credentials object containing the user's access and refresh tokens.
  If the authentication fails, it returns None.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  try:
    if os.path.exists("token.json"):
      creds = Credentials.from_authorized_user_file("token.json", SCOPES)
      print(f"Token loaded from {os.path.abspath('token.json')}")
      if creds.valid:
        print("Token is valid, Gmail API can be accessed.\n")
        return creds
    else:
      print("Token file not found. Please authenticate.")
  except ValueError as e:
    print(f"Error loading token: {e}")
  except FileNotFoundError as e:
    print(f"Token file not found: {e}")
  except json.JSONDecodeError as e:
    print(f"Error decoding token JSON: {e}")
  except TypeError as e:
    print(f"Error loading token: {e}")
  except Exception as e:
    print(f"Error loading token: {e}")

  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
        "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
      
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())
      print(f"Token saved to {os.path.abspath('token.json')}")

def test_gmail_api(creds):
  """
  Test the Gmail API by listing the user's labels.
  This function is called after the user has authenticated and the token has been saved.
  It uses the credentials to access the Gmail API and list the user's labels.
  If the API call is successful, it prints the labels to the console.
  
  Parameters:
  creds (Credentials): The credentials object containing the user's access and refresh tokens.
  """
  try:
    
    if creds:
      # Call the Gmail API
      service = build("gmail", "v1", credentials=creds)
      results = service.users().labels().list(userId="me").execute()

      print("-" * 20)
      print("Gmail API is working !")
      print("Trying to list labels...")

      # Call the Gmail API to list labels
      labels = results.get("labels", [])

      if not labels:
        print("No labels found.")
        return
      print("\nAll labels found :\n")
      for label in labels:
        print(label["name"])
    else:
      print("No valid credentials found. Please authenticate.")
      return
    
  except FileNotFoundError as e:
    print(f"File not found: {e}")
  except HttpError as error:
    # TODO(developer) - Handle errors from gmail API.
    print(f"An error occurred: {error}")
  except Exception as e:
    print(f"An error occurred: {e}")

def get_unread_emails(creds):
  """
  Get unread emails from the user's Gmail inbox using the Gmail API.
  This function retrieves unread emails from the user's inbox and return the message IDs to the console.

  Parameters:
  creds (Credentials): The credentials object containing the user's access and refresh tokens.
  """
  try:
    service = build("gmail", "v1", credentials=creds)
    results = service.users().messages().list(userId="me", labelIds=["INBOX", "UNREAD"]).execute()
    messages = results.get("messages", [])

    return messages

  except HttpError as error:
    print(f"An HTTP error occurred while getting unread emails : {error}")
    return
  except Exception as e:
    print(f"An error occured while getting unread emails : {e}")
    return
  
def get_sender_email(creds, message_id):
  """
  Get the sender's email address from a specific email message using the Gmail API.

  Parameters:
  creds (Credentials): The credentials object containing the user's access and refresh tokens.
  message_id (str): The ID of the email message to retrieve.

  Returns:
  str: The sender's email address if found, otherwise None.
  """
  try:
    service = build("gmail", "v1", credentials=creds)
    message = service.users().messages().get(userId="me", id=message_id).execute()
    headers = message["payload"]["headers"]

    for header in headers:
      if header["name"] == "From":
        sender = header["value"].split("<")[-1].split(">")[0]
        return sender
    return None

  except HttpError as error:
    print(f"An HTTP error occurred while getting sender email : {error}")
    return None
  except Exception as e:
    print(f"An error occurred while getting sender email : {e}")
    return None
  
def get_email_subject(creds, message_id):
  """
  Get the subject of a specific email message using the Gmail API.

  Parameters:
  creds (Credentials): The credentials object containing the user's access and refresh tokens.
  message_id (str): The ID of the email message to retrieve.

  Returns:
  str: The subject of the email if found, otherwise None.
  """
  try:
    service = build("gmail", "v1", credentials=creds)
    message = service.users().messages().get(userId="me", id=message_id).execute()
    headers = message["payload"]["headers"]

    for header in headers:
      if header["name"] == "Subject":
        return header["value"]
    return None

  except HttpError as error:
    print(f"An HTTP error occurred while getting email subject : {error}")
    return None
  except Exception as e:
    print(f"An error occurred while getting email subject : {e}")
    return None
  
def get_email_domain(creds, message_id):
  """
  Get the domain of the sender's email address from a specific email message using the Gmail API.

  Parameters:
  creds (Credentials): The credentials object containing the user's access and refresh tokens.
  message_id (str): The ID of the email message to retrieve.

  Returns:
  str: The domain of the sender's email if found, otherwise None.
  """
  try:
    sender = get_sender_email(creds, message_id)
    if sender:
      domain = sender.split("@")[-1].split(">")[0]
      return domain
    return None

  except Exception as e:
    print(f"An error occurred while getting email domain : {e}")
    return None
  
def is_promo_email(creds, message_id):
  """
  Check if a specific email message is a promotion email using the Gmail API.

  Parameters:
  creds (Credentials): The credentials object containing the user's access and refresh tokens.
  message_id (str): The ID of the email message to check.

  Returns:
  bool: True if the email is a promotion, False otherwise.
  """
  try:
    service = build("gmail", "v1", credentials=creds)
    message = service.users().messages().get(userId="me", id=message_id).execute()
    labels = message["labelIds"]

    PROMOTIONAL_SENDERS_FILE = config.PROMOTIONAL_SENDERS_FILE
    PROMOTIONAL_SUBJECTS_FILE = config.PROMOTIONAL_SUBJECTS_FILE
    PROMOTIONAL_DOMAINS_FILE = config.PROMOTIONAL_DOMAINS_FILE

    sender = get_sender_email(creds, message_id)
    subject = get_email_subject(creds, message_id)
    domain = get_email_domain(creds, message_id)
    if sender and subject and domain:
      promotional_senders = utils.read_file(PROMOTIONAL_SENDERS_FILE)
      promotional_subjects = utils.read_file(PROMOTIONAL_SUBJECTS_FILE)
      promotional_domains = utils.read_file(PROMOTIONAL_DOMAINS_FILE)

      # Check if the email has any promotional keywords in the sender, subject, or domain
      if any(keyword.lower() in sender.lower() for keyword in promotional_senders):
        print(f"Sender: {sender} is a promotional sender.")
        return True
      if any(keyword.lower() in subject.lower() for keyword in promotional_subjects):
        print(f"Subject: {subject} is a promotional subject.")
        return True
      if any(keyword.lower() in domain.lower() for keyword in promotional_domains):
        print(f"Domain: {domain} is a promotional domain.")
        return True
      
    # Check if the email has the "CATEGORY_PROMOTIONS" label
    if "CATEGORY_PROMOTIONS" in labels:
      return True

    return False

  except HttpError as error:
    print(f"An HTTP error occurred while checking for promotion email : {error}")
    return False
  except Exception as e:
    print(f"An error occurred while checking for promotion email : {e}")
    return False
  
def get_label_id(creds, label_name):
  """
  Get the ID of a specific label using the Gmail API.

  Parameters:
  creds (Credentials): The credentials object containing the user's access and refresh tokens.
  label_name (str): The name of the label to retrieve.

  Returns:
  str: The ID of the label if found, otherwise None.
  """
  try:
    service = build("gmail", "v1", credentials=creds)
    results = service.users().labels().list(userId="me").execute()
    labels = results.get("labels", [])

    for label in labels:
      if label["name"] == label_name:
        return label["id"]
    return None

  except HttpError as error:
    print(f"An HTTP error occurred while getting label ID : {error}")
    return None
  except Exception as e:
    print(f"An error occurred while getting label ID : {e}")
    return None
  
def apply_label(creds, message_id, label_name):
  """
  Apply a label to a specific email message using the Gmail API.
  This function modifies the email message by adding the specified label ID to it.

  Parameters:
  creds (Credentials): The credentials object containing the user's access and refresh tokens.
  message_id (str): The ID of the email message to modify.
  label_name (str): The name of the label to apply to the email message.

  Returns:
  bool: True if the label was successfully applied, False otherwise.
  """
  try:
    service = build("gmail", "v1", credentials=creds)
    label_id = get_label_id(creds, label_name)

    if label_id:
      # Apply the label to the email message
      service.users().messages().modify(
        userId="me",
        id=message_id,
        body={"addLabelIds": [label_id]}
      ).execute()
      print(f"Label '{label_name}' applied to message ID: {message_id}")
      return True
    else:
      print(f"Label '{label_name}' not found.")
      return False

  except HttpError as error:
    print(f"An HTTP error occurred while applying label : {error}")
    return False
  except Exception as e:
    print(f"An error occurred while applying label : {e}")
    return False