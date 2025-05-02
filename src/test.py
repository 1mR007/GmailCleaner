import src.mail_handler as mail_handler

authenticator = mail_handler.Authenticator()
creds = authenticator.authenticate()
if not creds:
    print("[bold red]Failed to authenticate. Please check your credentials.[/bold red]")
    exit(1)

manager = mail_handler.EmailManager(creds)
print("Gmail API authenticated successfully.")

messages = manager.get_unread_emails_ids()

if not messages:
    print("[yellow]No unread emails found.[/yellow]")
else:
    print(f"[bold green]Found {len(messages)} unread emails.[/bold green]")
    for message_id in messages:
        details = manager.batch_get_email_details(message_id)
        sender = details.get("sender", "Unknown Sender")
        subject = details.get("subject", "No Subject")
        domain = sender.split('@')[-1] if '@' in sender else "Unknown Domain"
        print(f"Subject : {subject}")
        print(f"Sender : {sender}")
        print(f"Domain : {domain}")
        print("-" * 40)
        if manager.is_promo_email(message_id):
            print(f"[bold red]This email is promotional.[/bold red]")
        else:
            print(f"[bold green]This email is not promotional.[/bold green]")