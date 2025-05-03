# src/config.py

import os

class Config:
    """
    Configuration class for GmailCleaner application.
    """
    def __init__(self):
        # Définir le chemin vers le dossier logs
        self.LOGS_DIR = "./logs"
        
        # Créer le dossier logs s'il n'existe pas
        os.makedirs(self.LOGS_DIR, exist_ok=True)
        
        # Application configuration
        self.TARGET_FOLDER = "GmailCleaner"
        self.PROMOTIONAL_SENDERS_FILE = os.path.join(self.LOGS_DIR, "promotional_senders.txt")
        self.PROMOTIONAL_SUBJECTS_FILE = os.path.join(self.LOGS_DIR, "promotional_subjects.txt")
        self.PROMOTIONAL_DOMAINS_FILE = os.path.join(self.LOGS_DIR, "promotional_domains.txt")

        # Paramètres de performance
        self.BATCH_SIZE = 100

config = Config()