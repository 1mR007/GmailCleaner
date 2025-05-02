# src/utils.py

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
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return [line.strip() for line in file.readlines()]
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return []
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return []

    @staticmethod
    def write_to_file(file_path, content, append=True):
        """
        Write content to a file.
        """
        try:
            mode = 'a' if append else 'w'
            with open(file_path, mode, encoding='utf-8') as file:
                file.write(content)
            return True
        except Exception as e:
            print(f"Error writing to file {file_path}: {e}")
            return False