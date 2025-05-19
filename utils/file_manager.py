import os
import shutil


class FileManager:

    def ensure_directory_exists(path):
        """Garante que um diretório existe, criando-o se necessário."""
        if not os.path.exists(path):
            os.makedirs(path)

    def create_directory(self, path):
        """Create a directory if it doesn't exist"""
        os.makedirs(path, exist_ok=True)

    def write_file(self, path, content):
        """Write content to a file, creating directories as needed"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)

    def copy_file(self, src, dest):
        """Copy a file from source to destination"""
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(src, dest)

    def file_exists(self, path):
        """Check if a file exists"""
        return os.path.isfile(path)