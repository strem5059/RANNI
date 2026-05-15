import os
import shutil
from pathlib import Path
from core.utils.logger import ranni_logger

class FileManager:
    def __init__(self, allowed_dirs=None):
        self.logger = ranni_logger.bind(module="files")
        self.allowed_dirs = allowed_dirs or []

    def _resolve_path(self, path):
        path = os.path.expandvars(path)
        path = os.path.expanduser(path)
        return os.path.abspath(path)

    def _is_path_allowed(self, path):
        if not self.allowed_dirs:
            return True
        abs_path = self._resolve_path(path)
        for allowed in self.allowed_dirs:
            allowed_abs = self._resolve_path(allowed)
            if abs_path.startswith(allowed_abs):
                return True
        return False

    def read_file(self, path, encoding="utf-8"):
        if not self._is_path_allowed(path):
            return None, "Permiso denegado"
        try:
            with open(self._resolve_path(path), "r", encoding=encoding) as f:
                return f.read(), None
        except Exception as e:
            return None, str(e)

    def write_file(self, path, content, encoding="utf-8"):
        if not self._is_path_allowed(path):
            return False, "Permiso denegado"
        try:
            abs_path = self._resolve_path(path)
            Path(abs_path).parent.mkdir(parents=True, exist_ok=True)
            with open(abs_path, "w", encoding=encoding) as f:
                f.write(content)
            return True, None
        except Exception as e:
            return False, str(e)

    def list_directory(self, path="."):
        try:
            abs_path = self._resolve_path(path)
            entries = []
            for entry in os.scandir(abs_path):
                entries.append({
                    "name": entry.name,
                    "path": entry.path,
                    "is_dir": entry.is_dir(),
                    "size": entry.stat().st_size if entry.is_file() else 0,
                    "modified": entry.stat().st_mtime
                })
            return entries, None
        except Exception as e:
            return None, str(e)

    def delete_file(self, path):
        if not self._is_path_allowed(path):
            return False, "Permiso denegado"
        try:
            os.remove(self._resolve_path(path))
            return True, None
        except Exception as e:
            return False, str(e)

    def create_directory(self, path):
        try:
            Path(self._resolve_path(path)).mkdir(parents=True, exist_ok=True)
            return True, None
        except Exception as e:
            return False, str(e)
