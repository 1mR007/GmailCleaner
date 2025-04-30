# src/mail_handler.py

import config
import utils
import imaplib
import email

def gmail_connect():
    """
    Connect to Gmail using IMAP and return the connection object.
    """
    try:
        mail = imaplib.IMAP4_SSL(config.IMAP_SERVER, config.IMAP_PORT)
        mail.login(config.EMAIL_ADDRESS, config.APP_PASSWORD)
        return mail
    except Exception as e:
        print(f"Error while logging to Gmail: {e}")

def close_connection(mail):
    """
    Close the mail connection properly.
    """
    if mail:
        try:
            mail.close()
            mail.logout()
        except Exception as e:
            print(f"Error during logout: {e}")

def search_unseen_emails(mail, mode="UNSEEN", fallback_mode="ALL"):
    """
    Search for unseen emails in the inbox based on the mode. If no emails are found using the given mode,
    it will search using the fallback mode.
    
    Parameters:
    - mode: Primary search mode (e.g., 'UNSEEN', 'ALL', etc.).
    - fallback_mode: Fallback search mode if the primary search fails (default is 'ALL').
    
    Returns a list of email IDs.
    """
    try:
        mail.select()
        typ, data = mail.search(None, mode)
        print(f"Search status: {typ}, Data: {data}")
        if typ == 'OK' and data[0]:
            if data[0] == b'':
                print(f"No emails found using mode '{mode}'. Trying fallback mode '{fallback_mode}'...")
                typ, data = mail.search(None, fallback_mode)
            return data[0].split()
        else:
            print(f"Failed to search for emails using mode '{mode}'.")
            return []
    except Exception as e:
        print(f"Error searching emails: {e}")
        return []
def fetch_email_by_id(connection, email_id):
    """
    Fetch an email by its ID.
    """
    try:
        typ, data = connection.fetch(email_id, '(RFC822)')
        if typ == 'OK':
            return email.message_from_bytes(data[0][1])
        else:
            print(f"Failed to fetch email with ID {email_id}.")
            return None
    except Exception as e:
        print(f"Error fetching email: {e}")
        return None
    
def is_promotional(subject, sender):
    """
    Check if the email is promotional based on the subject and sender.
    """
    if not subject or not sender:
        return False
    
    promotional_subjects_file = config.PROMOTIONAL_SUBJECTS_FILE
    promotional_senders_file = config.PROMOTIONAL_SENDERS_FILE
    promotional_domains_file = config.PROMOTIONAL_DOMAINS_FILE

    local_part = sender.split('@')[0]
    domain_part = sender.split('@')[1] if '@' in sender else ''

    promotional_subjects = utils.read_file(promotional_subjects_file)
    promotional_senders = utils.read_file(promotional_senders_file)
    promotional_domains = utils.read_file(promotional_domains_file)

    # Check if the subject or sender matches any promotional criteria
    for promo_subject in promotional_subjects:
        if promo_subject.lower() in subject.lower():
            return True
    for promo_sender in promotional_senders:
        if promo_sender.lower() in local_part.lower():
            return True
    for promo_domain in promotional_domains:
        if promo_domain.lower() in domain_part.lower():
            return True
        
    # If no matches found, return False 
    return False