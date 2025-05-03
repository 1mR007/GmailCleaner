# src/utils.py

import os

class Utils:
    """
    Utility class for GmailCleaner application.
    """
    @staticmethod
    def display_summary(processed, promotional_count):
        """
        Display a summary of the email processing.
        """
        print(f"\nSummary:")
        print(f"Total emails processed: {processed}")
        print(f"Promotional emails found: {promotional_count}")

    @staticmethod
    def read_file(file_path):
        """
        Read the contents of a file and return it as a list of lines.
        Creates the file if it doesn't exist.
        """
        try:
            # Vérifier si le fichier existe
            if not os.path.exists(file_path):
                # Créer le dossier parent si nécessaire
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                # Créer un fichier vide
                with open(file_path, 'w', encoding='utf-8') as file:
                    pass
                return []
                
            # Lire le fichier s'il existe
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = [line.strip() for line in file.readlines() if line.strip()]
                return lines
                
        except FileNotFoundError:
            print(f"File not found: {file_path}. Creating an empty file.")
            # Créer le dossier parent si nécessaire
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Créer un fichier vide
            with open(file_path, 'w', encoding='utf-8') as file:
                pass
            return []
            
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return []

    @staticmethod
    def write_to_file(file_path, content, append=True):
        """
        Write content to a file.
        Creates the file and parent directories if they don't exist.
        """
        try:
            # Créer le dossier parent si nécessaire
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Écrire dans le fichier
            mode = 'a' if append else 'w'
            with open(file_path, mode, encoding='utf-8') as file:
                file.write(content)
            return True
            
        except Exception as e:
            print(f"Error writing to file {file_path}: {e}")
            return False
            
    @staticmethod
    def ensure_directory_exists(path):
        """
        Ensure that the directory exists, create it if it doesn't.
        """
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating directory {path}: {e}")
            return False