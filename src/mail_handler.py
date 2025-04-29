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
    
def decode_email_body(msg):
    try:
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        payload = part.get_payload(decode=True)
                        if payload is None:
                            continue
                            
                        charset = part.get_content_charset()
                        if charset:
                            body += payload.decode(charset, errors="replace") # Concatenate each part of the multipart msg
                        else:
                            # Try common encodings
                            for encoding in ['utf-8', 'latin-1', 'ascii']:
                                try:
                                    body += payload.decode(encoding, errors="replace") # Concatenate each part of the multipart msg
                                    break
                                except UnicodeDecodeError:
                                    continue
                                    
                        # Handle quoted-printable encoding
                        if part.get('Content-Transfer-Encoding', '').lower() == 'quoted-printable':
                            body = quopri.decodestring(body.encode()).decode('utf-8', errors='replace')
                            
                    except Exception as e:
                        print(f"Error decoding part: {e}")
                        continue
        else:
            payload = msg.get_payload(decode=True)
            if payload is not None:
                charset = msg.get_content_charset()
                if charset:
                    body = payload.decode(charset, errors="replace")
                else:
                    # Try common encodings
                    for encoding in ['utf-8', 'latin-1', 'ascii']:
                        try:
                            body = payload.decode(encoding, errors="replace")
                            break
                        except UnicodeDecodeError:
                            continue

        return body if body else None
    except Exception as e:
        print(f"Error while decoding email's body: {e}")
        return None
    
def fetch_recent_emails(mail, email_range):
    try:
        # Get all email IDs
        _, email_ids = mail.search(None, 'ALL')
        
        if email_ids[0]:
            for i in range(1, email_range + 1):
                msg_id = email_ids[0].split()[-i] # Fetch email_ids in the given email_range
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