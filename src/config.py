# src/config.py

import os
from dotenv import load_dotenv

class Config:
    """
    Configuration class for GmailCleaner application.
    """
    def __init__(self):
        # Path to the .env file
        self.ENV_PATH = "./logs/.env"
        
        # Load .env variables
        load_dotenv(self.ENV_PATH)
        
        # Gmail configuration
        self.EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
        self.APP_PASSWORD = os.getenv("APP_PASSWORD")
        self.IMAP_SERVER = os.getenv("IMAP_SERVER")
        self.IMAP_PORT = int(os.getenv("IMAP_PORT", 993))
        
        # Application configuration
        self.TARGET_FOLDER = os.getenv("TARGET_FOLDER", "GmailCleaner")
        self.PROMOTIONAL_SENDERS_FILE = "./logs/promotional_senders.txt"
        self.PROMOTIONAL_SUBJECTS_FILE = "./logs/promotional_subjects.txt"
        self.PROMOTIONAL_DOMAINS_FILE = "./logs/promotional_domains.txt"

config = Config()