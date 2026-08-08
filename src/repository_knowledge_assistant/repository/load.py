from pathlib import Path
from typing import List
from .utils import RawDocument


class RepositoryLoader:

    SUPPORTED_EXTENSIONS = {
        # Documentation
        ".md", ".rst", ".txt",

        # Code
        ".py", ".js", ".jsx", ".ts", ".tsx",
        ".java", ".kt", ".scala", ".go",
        ".rs", ".c", ".cpp", ".h", ".hpp", ".cs",
        ".php", ".rb", ".r", ".f90", ".f95",
        ".m", ".jl", ".swift", ".lua", ".pl"

        # Configuration and data
        ".yaml", ".yml", ".toml", ".ini",
        ".cfg", ".json", ".xml"

        # Scripts
        ".sh", ".bash"

        # Notebooks
        ".ipynb"
    }

    IGNORED_DIRECTORIES = {
        ".git",
        "__pycache__",
        ".venv",
        "venv",
        "node_modules",
        "dist",
        "build",
        "target",
        "out",
        ".idea",
        ".vscode",
        ".pytest_cache",
        ".mypy_cache",
        ".cache"
    }

    def load(self, repo_path: Path) -> List[RawDocument]:
        """
        Load all supported files from repository.
        """ 
        documents = []

        for i, file_path in enumerate(repo_path.rglob("*")):

            if not file_path.is_file():
                continue
            
            if self._ignore(file_path):
                continue
            
            if not self._is_supported(file_path):
                continue
            
            try:
                text = file_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue

            documents.append(
                RawDocument(file_path, text, file_path.suffix, file_path.name, f"r{str()}")
            )

        return documents

    def _ignore(self, path: Path) -> bool:

        if any(part in self.IGNORED_DIRECTORIES for part in path.parts):
            return True

        return False

    def _is_supported(self, path: Path) -> bool:
        return path.suffix in self.SUPPORTED_EXTENSIONS