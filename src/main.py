# src/main.py

import mail_handler

def main():
    try:
        mail = mail_handler.gmail_connect()
        if mail:
            status, messages = mail.select()
            if status == "OK":
                print("Inbox is accessible.")
                mail_handler.fetch_recent_emails(mail, 5)
            else:
                print("Inbox is not accessible.")
                try:
                    mail.close()
                    mail.logout()
                except Exception as e:
                    print(f"Error during logout: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    print("Running script...")
    main()