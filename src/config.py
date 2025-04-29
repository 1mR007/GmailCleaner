# src/config.py

from dotenv import load_dotenv
import os

ENV_PATH = "./logs/.env"

# Load .env variables
load_dotenv(ENV_PATH)

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
APP_PASSWORD = os.getenv("APP_PASSWORD")
IMAP_SERVER = os.getenv("IMAP_SERVER")
IMAP_PORT = int(os.getenv("IMAP_PORT", 993))
TARGET_FOLDER = os.getenv("TARGET_FOLDER", "MailCleaner")