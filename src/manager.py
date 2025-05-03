# src/manager.py

import time
import random

from src.config import config
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from rich.progress import Progress, TextColumn, BarColumn, TimeRemainingColumn, SpinnerColumn

class EmailManager:
    """
    Handles email-related operations using Gmail API.
    """

    BATCH_SIZE = config.BATCH_SIZE

    def __init__(self, creds, label_name=None):
        self.creds = creds
        self.label_name = label_name if label_name else config.TARGET_FOLDER
        self.service = build("gmail", "v1", credentials=creds)

    def get_emails_ids(self):
        """
        Retrieve unread emails from the inbox.
        Returns a list of message IDs.
        """
        try:
            results = self.service.users().messages().list(userId="me", maxResults=100, q=f"-label:{self.label_name if self.label_name else "GmailCleaner"}").execute()
            return results.get("messages", [])
        except HttpError as error:
            print(f"An HTTP error occurred while getting unread emails: {error}")
            return []
    
    @staticmethod
    def api_request_with_retry(request_func, max_retries=5, base_delay=1):
        """
        Execute an API request with exponential backoff retry logic.
        
        Args:
            request_func: A function that executes the actual API request
            max_retries: Maximum number of retry attempts
            base_delay: Base delay for exponential backoff in seconds
        
        Returns:
            The result of the API request if successful
        """
        for retry in range(max_retries):
            try:
                return request_func()
            except HttpError as e:
                if e.resp.status == 429 and retry < max_retries - 1:
                    wait_time = base_delay * (2 ** retry) + random.uniform(0, 1)
                    print(f"Rate limited. Retrying in {wait_time:.2f} seconds...")
                    time.sleep(wait_time)
                else:
                    raise
        
    def batch_get_email_metadata(self, message_ids, progress=None, progress_task=None, max_retries=5, batch_size=BATCH_SIZE):
        """
        Récupère les métadonnées en lot avec possibilité de passer une barre de progression externe
        Args:
            message_ids: Liste des IDs de messages
            progress: Instance Progress existante (optionnelle)
            progress_task: ID de tâche dans l'instance Progress (optionnel)
            max_retries: Nombre maximum de tentatives
            batch_size: Taille des lots
        """
        results = {}
        total_messages = len(message_ids)
        
        # Si aucune barre de progression n'est fournie, en créer une nouvelle
        if progress is None:
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}[/bold blue]"),
                BarColumn(bar_width=40),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TextColumn("({task.completed}/{task.total})"),
                TimeRemainingColumn(),
            ) as local_progress:
                task = local_progress.add_task("[green]Retrieving metadata...", total=total_messages)
                for i in range(0, total_messages, batch_size):
                    chunk = message_ids[i:i + batch_size]
                    batch_results = self.execute_batch_with_retry(chunk, max_retries)
                    results.update(batch_results)
                    local_progress.update(task, advance=len(chunk))
                    adaptive_delay = min(5, 1 + (i / total_messages) * 2)
                    time.sleep(adaptive_delay)
        # Sinon, utiliser la barre de progression fournie
        else:
            for i in range(0, total_messages, batch_size):
                chunk = message_ids[i:i + batch_size]
                batch_results = self.execute_batch_with_retry(chunk, max_retries)
                results.update(batch_results)
                if progress is not None and progress_task is not None:
                    # Assurez-vous que progress_task est bien un ID de tâche (int) et non une fonction
                    progress.update(progress_task, advance=len(chunk))
                adaptive_delay = min(5, 1 + (i / total_messages) * 2)
                time.sleep(adaptive_delay)
                
        return results
    
    def execute_batch_with_retry(self, chunk, max_retries=5):
        """
        Execute a batch request with retry logic.
        """
        batch_results = {}

        def callback(request_id, response, exception):
            if exception:
                print(f"An error occurred while getting email metadata for {request_id}: {exception}")
            else:
                message_id = response["id"]
                headers = response.get("payload", {}).get("headers", [])
                labels = response.get("labelIds", [])

                sender, subject = "", ""
                for header in headers:
                    if header["name"] == "From":
                        sender = header["value"]
                        sender = sender.split("<")[-1].split(">")[0] if "<" in sender else sender
                    elif header["name"] == "Subject":
                        subject = header["value"]

                batch_results[message_id] = {
                    "id": message_id,
                    "sender": sender,
                    "subject": subject,
                    "labels": labels
                }

        def execute_request():
            batch = self.service.new_batch_http_request()
            for message in chunk:
                message_id = message["id"]
                if not message_id:
                    continue

                batch.add(self.service.users().messages().get(
                    userId="me",
                    id=message_id,
                    format="metadata",
                    metadataHeaders=["Subject", "From"]
                ), callback=callback)
                
            batch.execute()
    
        # Utiliser la méthode statique correctement
        self.__class__.api_request_with_retry(execute_request, max_retries)
        return batch_results
    
    def is_promo_email(self, rules, meta):
        """
        Check if an email is promotional based on sender, subject, or domain.
        Returns a tuple (is_promotional, reason)
        """
        try:
            # Vérifier que meta est bien un dictionnaire
            if not isinstance(meta, dict):
                print(f"Warning: meta is not a dictionary: {meta}")
                return False
                
            sender = meta.get("sender", "").lower()
            subject = meta.get("subject", "").lower()
            labels = meta.get("labels", [])

            promotional_senders = [s.lower() for s in rules[0]]
            promotional_subjects = [s.lower() for s in rules[1]]
            promotional_domains = [s.lower() for s in rules[2]]

            # Extraire le domaine de l'email
            domain = ""
            if sender and "@" in sender:
                domain = sender.split("@")[-1].split(">")[0].lower()

            # Vérification par expéditeur
            for promo_sender in promotional_senders:
                if promo_sender and promo_sender in sender:
                    return True

            # Vérification par sujet
            for promo_subject in promotional_subjects:
                if promo_subject and promo_subject in subject:
                    return True

            # Vérification par domaine
            for promo_domain in promotional_domains:
                if promo_domain and domain and promo_domain in domain:
                    return True

            # Vérification par label Gmail
            if "CATEGORY_PROMOTIONS" in labels:
                return True
                
            # Vérifier les mots-clés communs de promotion dans le sujet
            promo_keywords = ["offre", "promo", "discount", "sale", "deal", "newsletter", 
                            "special", "coupon", "off", "save", "free", "gratuit"]
            for keyword in promo_keywords:
                if keyword in subject:
                    return True

            return False
        except Exception as e:
            print(f"An error occurred while checking for promotion email: {e}")
            return False
        
    def batch_apply_label(self, email_ids, label_name=None, progress=None, progress_task=None, batch_size=BATCH_SIZE):
        """
        Apply a label to a batch of email IDs.
        Returns True if successful, False otherwise.
        """
        if label_name is None:
            label_name = self.label_name
        
        label_id = self.get_label_id()
        
        if not label_id:
            print(f"Label '{label_name}' couldn't be created or found.")
            return False
        
        if not progress:
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}[/bold blue]"),
                BarColumn(bar_width=40),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TextColumn("({task.completed}/{task.total})"),
                TimeRemainingColumn(),
            ) as progress:
                task = progress.add_task("[green]Applying labels...", total=len(email_ids))
                
                for i in range(0, len(email_ids), batch_size):
                    chunk = email_ids[i:i + batch_size]
                    chunk_ids = [msg["id"] for msg in chunk if isinstance(msg, dict) and "id" in msg]
                    
                    if not chunk_ids:
                        progress.update(task, advance=len(chunk))
                        continue
                    
                    def execute_request():
                        return self.service.users().messages().batchModify(
                            userId="me",
                            body={
                                "ids": chunk_ids,
                                "addLabelIds": [label_id]
                            }
                        ).execute()
                    
                    try:
                        # Utiliser correctement la méthode statique
                        self.__class__.api_request_with_retry(execute_request)
                        progress.update(task, advance=len(chunk))
                        
                        # Délai adaptatif pour éviter les limitations de l'API
                        adaptive_delay = 1 + random.uniform(0.5, 1.5)
                        time.sleep(adaptive_delay)
                        
                    except Exception as e:
                        print(f"Error applying label to batch {i}: {e}")
                        # Continuer avec le batch suivant au lieu de terminer immédiatement
                        progress.update(task, advance=len(chunk))
        
            # Si nous arrivons ici, tout s'est bien passé
            return True
        else:
            if progress is not None and progress_task is not None:
                for i in range(0, len(email_ids), batch_size):
                    chunk = email_ids[i:i + batch_size]
                    chunk_ids = [msg["id"] for msg in chunk if isinstance(msg, dict) and "id" in msg]
                    
                    if not chunk_ids:
                        progress.update(progress_task, advance=len(chunk))
                        continue
                    
                    def execute_request():
                        return self.service.users().messages().batchModify(
                            userId="me",
                            body={
                                "ids": chunk_ids,
                                "addLabelIds": [label_id]
                            }
                        ).execute()
                    
                    try:
                        # Utiliser correctement la méthode statique
                        self.__class__.api_request_with_retry(execute_request)
                        progress.update(progress_task, advance=len(chunk))
                        
                        # Délai adaptatif pour éviter les limitations de l'API
                        adaptive_delay = 1 + random.uniform(0.5, 1.5)
                        time.sleep(adaptive_delay)
                        
                    except Exception as e:
                        print(f"Error applying label to batch {i}: {e}")
                        # Continuer avec le batch suivant au lieu de terminer immédiatement
                        progress.update(progress_task, advance=len(chunk))
                return True

    def get_label_id(self):
        """
        Retrieve the ID of a specific label.
        """
        try:
            results = self.service.users().labels().list(userId="me").execute()
            labels = results.get("labels", [])
            for label in labels:
                if label["name"] == self.label_name:
                    return label["id"]
                    
            # If label doesn't exist, create it
            return self.create_label()
        except HttpError as error:
            print(f"An HTTP error occurred while getting label ID: {error}")
            return None
            
    def create_label(self):
        """
        Create a new label if it doesn't exist.
        """
        try:
            label = self.service.users().labels().create(
                userId="me",
                body={
                    "name": self.label_name,
                    "labelListVisibility": "labelShow",
                    "messageListVisibility": "show"
                }
            ).execute()
            print(f"Label '{self.label_name}' created successfully.")
            return label["id"]
        except HttpError as error:
            print(f"An HTTP error occurred while creating label: {error}")
            return None