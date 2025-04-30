import email
import mail_handler

mail = mail_handler.gmail_connect()
if mail:
    print("Connected to Gmail successfully.")
else:
    print("Failed to connect to Gmail.")

subject = "Vous avez téléchargé le modèle Student OS depuis Notion"
sender = "marketplace@mail.notion.so"

print(mail_handler.is_promotional(subject, sender))  # Expected output: True
print(mail_handler.is_promotional("Hello World", ""))  # Expected output: False