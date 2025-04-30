import os
from dotenv import load_dotenv

ENV_PATH = "./logs/.env"  # Path to the .env file

# Load .env variables
load_dotenv(ENV_PATH)

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
APP_PASSWORD = os.getenv("APP_PASSWORD")
IMAP_SERVER = os.getenv("IMAP_SERVER")
IMAP_PORT = int(os.getenv("IMAP_PORT", 993))
TARGET_FOLDER = os.getenv("TARGET_FOLDER", "GmailCleaner")
PROMOTIONAL_SENDERS_FILE = "logs/promotional_senders.txt"
PROMOTIONAL_SUBJECTS_FILE = "logs/promotional_subjects.txt"
PROMOTIONAL_DOMAINS_FILE = "logs/promotional_domains.txt"