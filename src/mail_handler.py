# src/mail_handler.py

import config
import imaplib
import quopri
import email

def gmail_connect():
    try:
        mail = imaplib.IMAP4_SSL(config.IMAP_SERVER, config.IMAP_PORT)
        mail.login(config.EMAIL_ADDRESS, config.APP_PASSWORD)
        mail.select()
        print(f"Successfully logged to Gmail.")
        return mail
    except Exception as e:
        print(f"Error while logging to Gmail: {e}")
    
def get_sender(mail_id, mail):
    """
    Get the sender email address from an email.
    """
    try:
        # Fetch the email headers
        _, msg_data = mail.fetch(mail_id, '(RFC822)')
        msg = email.message_from_bytes(msg_data[0][1])
        
        # Get the sender's email address
        sender = msg['From']
        return sender
    except Exception as e:
        print(f"Error getting sender: {e}")
        return None
    
def fetch_recent_emails(mail):
    try:
        # Get all email IDs
        _, email_ids = mail.search(None, 'ALL')
        
        if email_ids[0]:
            for msg_id in email_ids[0]:
                _, email_data = mail.fetch(msg_id, '(RFC822)')

                # Check the validity results of the previous fecth
                if email_data and email_data[0]:
                    email_body = email_data[0][1]
                    if email_body:
                        # Process the email only if the body is valid
                        print(f"Processing with the mail {i}: {msg_id}")
                        msg = email.message_from_bytes(email_body)
                        body = decode_email_body(msg)
                        if body:
                            print(f"Email body:\n{body}")
                        else:
                            print(f"Failed to decode email body for ID: {msg_id}")
                    else:
                        print(f"Empty email body for ID: {msg_id}")
                else:
                    print(f"Failed to fetch email data for ID: {msg_id}")
        else:
            print("No emails found.")
    except Exception as e:
        print(f"Error fetching emails: {e}")
        return False
    finally:
        try:
            mail.close()
            mail.logout()
        except Exception as e:
            print(f"Error closing connection: {e}")