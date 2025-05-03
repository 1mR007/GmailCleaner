# src/console.py

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, TextColumn, BarColumn, TimeRemainingColumn, SpinnerColumn
from rich.table import Table

from src.config import config
from src.utils import Utils
from src.authenticator import Authenticator
from src.manager import EmailManager


class CLIConsole:
    """
    A class to handle console output and user interaction.
    """

    def __init__(self):
        self.console = Console()
        self.authenticator = Authenticator()
        self.manager = None
        self.creds = None

    def authenticate(self):
        """Authenticate the user and initialize the email manager"""
        self.creds = self.authenticator.authenticate()
        if not self.creds:
            self.console.print("[bold red]Failed to authenticate.\nPlease check your credentials and/or your Internet connection.[/bold red]")
            exit(1)
        self.manager = EmailManager(self.creds)
        return self.creds

    def display_header(self):
        """Displays the application header with style"""
        self.console.print(Panel.fit(
            "[bold blue]GmailCleaner[/bold blue] [white]v1.0[/white]\n[italic]Smart cleaning for your Gmail inbox[/italic]",
            border_style="green",
            title="[yellow]GMailCleaner[/yellow]",
            subtitle="[cyan]Developed by 0xMR007[/cyan]",
        ))
        print("\n")

    def display_menu(self):
        """Displays the main menu and handles user choice"""
        self.console.print("\n[bold yellow]Main Menu[/bold yellow]")
        table = Table(show_header=False, box=None, padding=(0, 2, 0, 0))
        table.add_column(style="bold cyan")
        table.add_column()

        table.add_row("1", "Analyze unread emails")
        table.add_row("2", "Move promotional emails")
        table.add_row("3", "Manage detection rules")
        table.add_row("4", "View statistics")
        table.add_row("5", "Test Gmail API connection")
        table.add_row("0", "Exit")

        self.console.print(table)
        choice = Prompt.ask("\n[bold cyan]Your choice[/bold cyan]", choices=["0", "1", "2", "3", "4", "5"], default="1")
        return choice

    def process_emails(self, dry_run=False):
        """Version améliorée avec une seule instance Progress pour toutes les barres"""
        self.console.print(f"\n[bold]{'Analyzing' if dry_run else 'Processing'} unread emails...[/bold]")
        
        try:
            # Récupération des IDs des emails
            with self.console.status("[bold green]Retrieving unread emails...[/bold green]", spinner="dots"):
                messages = self.manager.get_emails_ids()

            if not messages:
                self.console.print("[yellow]No unread emails found.[/yellow]")
                return

            self.console.print(f"[green]✓[/green] {len(messages)} unread emails found.")
            processed_count, promo_count = 0, 0
            
            # Chargement des règles
            rules = [
                Utils.read_file(config.PROMOTIONAL_SENDERS_FILE),
                Utils.read_file(config.PROMOTIONAL_SUBJECTS_FILE),
                Utils.read_file(config.PROMOTIONAL_DOMAINS_FILE)
            ]

            promo_message_ids = []
            message_ids = [{"id": m["id"]} for m in messages]
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}[/bold blue]"),
                BarColumn(bar_width=40),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TextColumn("({task.completed}/{task.total})"),
            ) as progress:
                
                
                # Étape 1: Récupération des métadonnées
                metadata_task = progress.add_task("[green]Récupération des métadonnées...", total=len(messages))
                all_metadata = self.manager.batch_get_email_metadata(message_ids, progress=progress, progress_task=metadata_task)
                progress.update(metadata_task, completed=len(messages))
                
                # Étape 2: Analyse des emails
                analysis_task = progress.add_task("[green]Analyzing emails...", total=len(messages))
                
                for message in messages:
                    message_id = message["id"]
                    meta = all_metadata.get(message_id, {})
                    is_promo = self.manager.is_promo_email(rules, meta)
                    
                    if is_promo:
                        promo_count += 1
                        promo_message_ids.append(message)
                    
                    processed_count += 1
                    progress.update(analysis_task, advance=1)

                progress.update(analysis_task, completed=len(messages))
            
            # Affichage des résultats
            self.console.print("\n[bold green]Results:[/bold green]")
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Type")
            table.add_column("Count", justify="right")
            table.add_column("Action")
            table.add_row("Promotional emails", str(promo_count), f"[{'yellow' if dry_run else 'green'}]{'To move' if dry_run else 'Moved'}[/{'yellow' if dry_run else 'green'}]")
            table.add_row("Normal emails", str(processed_count - promo_count), "[blue]Kept[/blue]")
            self.console.print(table)
            
            if dry_run and promo_count > 0:
                move_now = Confirm.ask("\n[bold cyan]Do you want to move these promotional emails now?[/bold cyan]")
                if move_now:
                    
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[bold blue]{task.description}[/bold blue]"),
                        BarColumn(bar_width=40),
                        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    ) as move_progress:
                        move_task = move_progress.add_task("[green]Moving emails...", total=len(promo_message_ids))
                        success = self.manager.batch_apply_label(promo_message_ids, config.TARGET_FOLDER, progress=move_progress, progress_task=move_task)
                        move_progress.update(move_task, completed=len(promo_message_ids))
                    
                    if success:
                        self.console.print("[bold green]✓ Promotional emails have been moved successfully.[/bold green]")
                    else:
                        self.console.print("[bold red]✕ Some emails could not be moved. Check the logs for details.[/bold red]")
        
        except Exception as e:
            self.console.print(f"[bold red]Error while processing emails: {e}[/bold red]")

    def manage_detection_rules(self):
        """Manages the detection rules for promotional emails"""
        self.console.print("\n[bold yellow]Manage Detection Rules:[/bold yellow]")
        table = Table(show_header=False, box=None, padding=(0, 2, 0, 0))
        table.add_column(style="bold cyan")
        table.add_column()

        table.add_row("1", "View promotional senders")
        table.add_row("2", "View promotional subjects")
        table.add_row("3", "View promotional domains")
        table.add_row("4", "Add a promotional sender")
        table.add_row("5", "Add a promotional subject")
        table.add_row("6", "Add a promotional domain")
        table.add_row("0", "Return to main menu")

        self.console.print(table)
        choice = Prompt.ask("\n[bold cyan]Your choice[/bold cyan]", choices=["0", "1", "2", "3", "4", "5", "6"], default="0")

        if choice == "0":
            return
        elif choice == "1":
            self.view_file_content(config.PROMOTIONAL_SENDERS_FILE, "Promotional Senders")
        elif choice == "2":
            self.view_file_content(config.PROMOTIONAL_SUBJECTS_FILE, "Promotional Subjects")
        elif choice == "3":
            self.view_file_content(config.PROMOTIONAL_DOMAINS_FILE, "Promotional Domains")
        elif choice == "4":
            self.add_to_file(config.PROMOTIONAL_SENDERS_FILE, "promotional sender")
        elif choice == "5":
            self.add_to_file(config.PROMOTIONAL_SUBJECTS_FILE, "promotional subject")
        elif choice == "6":
            self.add_to_file(config.PROMOTIONAL_DOMAINS_FILE, "promotional domain")

        self.manage_detection_rules()

    def view_file_content(self, file_path, title):
        """Displays the content of a file"""
        lines = Utils.read_file(file_path)
        self.console.print(f"\n[bold green]{title}:[/bold green]")
        if not lines:
            self.console.print("[yellow]No entries found.[/yellow]")
            return
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("No.", style="dim", width=4)
        table.add_column(f"{title}")
        for i, line in enumerate(lines, 1):
            table.add_row(str(i), line)
        self.console.print(table)

    def add_to_file(self, file_path, entry_type):
        """Adds an entry to a file"""
        entry = Prompt.ask(f"[bold cyan]New {entry_type}[/bold cyan]")
        if entry:
            try:
                with open(file_path, 'a', encoding='utf-8') as file:
                    file.write(f"\n{entry}")
                self.console.print(f"[green]✓[/green] {entry_type.capitalize()} added successfully.")
            except Exception as e:
                self.console.print(f"[bold red]Error while adding: {e}[/bold red]")

    def show_statistics(self):
        """Displays usage statistics"""
        self.console.print("\n[bold yellow]Statistics:[/bold yellow]")
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Metric")
        table.add_column("Value", justify="right")
        table.add_row("Emails analyzed (total)", "0")
        table.add_row("Promotional emails moved", "0")
        table.add_row("Detection rate", "0%")
        self.console.print(table)
        self.console.print("\n[yellow]Note: Statistics are not yet implemented.[/yellow]")

    def test_gmail_connection(self):
        """Tests the connection to the Gmail API"""
        if not self.creds:
            self.console.print("[bold red]No valid credentials. Please authenticate.[/bold red]")
            return
        with self.console.status("[bold green]Testing Gmail API connection...[/bold green]", spinner="dots"):
            success = self.authenticator.test_gmail_api(self.manager.service)
            if success:
                self.console.print("[bold green]✓ Connection to Gmail API successful.[/bold green]")
            else:
                self.console.print("[bold red]✗ Connection to Gmail API failed.[/bold red]")