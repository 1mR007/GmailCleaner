# src/main.py

import os
import sys
from rich.prompt import Prompt

from src.console import CLIConsole


def main():
    """Main function of the program"""

    console = CLIConsole()
    
    try:
        # Display the header
        console.display_header()
        
        # Initialize credentials
        with console.console.status("[bold green]Connecting to Gmail API...[/bold green]", spinner="dots"):
            creds = console.authenticate()
        
        if not creds:
            console.console.print("[bold red]Failed to connect to Gmail API. Please check your credentials or try again.[/bold red]")
            sys.exit(1)
        
        # Main loop
        while True:
            choice = console.display_menu()
            
            if choice == "0":
                console.console.print("[bold green]Thank you for using GmailCleaner. See you soon ![/bold green]")
                break
            elif choice == "1":
                console.process_emails(dry_run=True)
            elif choice == "2":
                console.process_emails(dry_run=False)
            elif choice == "3":
                console.manage_detection_rules()
            elif choice == "4":
                console.show_statistics()
            elif choice == "5":
                console.test_gmail_connection()
            
            # Pause before returning to the menu
            if choice != "0":
                console.console.print()
                Prompt.ask("[bold cyan]Press [Enter] to continue[/bold cyan]")
                os.system('cls' if os.name == 'nt' else 'clear')
                console.display_header()
    
    except KeyboardInterrupt:
        console.console.print("\n[bold yellow]Program interrupted by the user.[/bold yellow]")
        sys.exit(0)
    except Exception as e:
        console.console.print(f"\n[bold red]An unexpected error occurred: {e}[/bold red]")
        sys.exit(1)


if __name__ == "__main__":
    main()