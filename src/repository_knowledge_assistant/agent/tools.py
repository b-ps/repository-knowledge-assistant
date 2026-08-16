from repository_knowledge_assistant.search.retrieve import Retriever
from typing import List
from pathlib import Path


def search_repository(query: str, retriever: Retriever, method: str = "hybrid") -> List[dict]:
    """
    Search the repository using the selected method retrieval.

    Args:
        query: Natural-language search query.
        retriever: Repository Retriever instance.
        method: Search method.

    Returns:
        Relevant repository chunks.
    """
    return retriever.retrieve(query=query, method=method)

def read_file(path: str, repository: str) -> str:
    """
    Read a file from the repository.

    Args:
        path: Relative path to the file.
        repository: Root directory of the repository.

    Returns:
        File contents.
    """
    root = Path(repository)
    file_path = (root / path)

    if not file_path.is_relative_to(root):
        raise ValueError("Path is outside the repository")

    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    return file_path.read_text(encoding="utf-8")