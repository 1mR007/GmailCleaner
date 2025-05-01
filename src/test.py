import mail_handler
import os

TARGET_FOLDER = mail_handler.config.TARGET_FOLDER  # Folder to move promotional emails to

try:
    creds = mail_handler.start_gmail_api()

    if creds:

        messages = mail_handler.get_unread_emails(creds)
        promos = 0

        if messages:
            for message in messages:
                sender = mail_handler.get_sender_email(creds, message["id"])
                subject = mail_handler.get_email_subject(creds, message["id"])
                domain = mail_handler.get_email_domain(creds, message["id"])
                if sender and subject and domain:
                    is_promo = mail_handler.is_promo_email(creds, message["id"])
                    if is_promo:
                        print(f"Promo email detected :\n")
                        print(f"Subject: {subject}")
                        print(f"Sender: {sender}")
                        print(f"Domain: {domain}")
                        promos += 1
                        # Move the email to the promotional folder
                        moved = mail_handler.apply_label(creds, message["id"], TARGET_FOLDER)
                        if moved:
                            print(f"Email moved to {TARGET_FOLDER} folder.")
                        else:
                            print(f"Failed to move email to {TARGET_FOLDER} folder.")
                    else:
                        print(f"Non-promo email detected :\n")
                        print(f"Subject: {subject}")
                        print(f"Sender: {sender}")
                        print(f"Domain: {domain}")
                else:
                    print("Failed to retrieve email details.")
                    continue
            mail_handler.utils.display_summary(len(messages), promos)
        else:
            print("No unread emails found.")
except KeyboardInterrupt:
    print("Process interrupted by user.")
    os._exit(0)
except Exception as e:
    print(f"An error occurred: {e}")
    os._exit(1)