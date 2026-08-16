from pathlib import Path
from urllib.parse import urlparse
from git import Repo

class RepositoryCloner:
    """Clone and update GitHub repositories in a local directory.
    
    Args:
        base_path: 
            Directory where the local copy of the repository will be stored.

    """

    base_path: Path

    def __init__(self, base_path: str = "data/repos"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def get_repository(self, url: str, update: bool = True) -> Path:
        """Get a local copy of a GitHub repository.

        If a local copy doesn't exist yet, clone the repository. 
        If it already exists, it can optionally be updated with ``git pull``.

        Args:
            url:
                URL of the GitHub repository.
            update:
                Whether to pull the latest changes of the repository when a local copy already exists. Default: ``True``.
        
        Returns:
            The path to the local copy of the repository.
        """
        repo_name = self._validate_repository(url)
        repo_path = self.base_path / repo_name

        if not repo_path.exists():
            self._clone_repository(url, repo_path)
        elif update:
            self._update_repository(repo_path)

        return repo_path

    def _validate_repository(self, url: str) -> str:
        """Validate a GitHub repository URL and extract its name.

        Args:
            url:
                Repository URL to validate.
        
        Returns:
            Repository name.
        """
        url = urlparse(url)

        if url.netloc != "github.com":
            raise ValueError("Only GitHub repositories are supported.")

        repo_name = Path(url.path).stem

        if not repo_name:
            raise ValueError("Invalid repository URL.")

        return repo_name

    def _clone_repository(self, url: str, repo_path: Path) -> None:
        """Clone the repository into a local directory.

        Args:
            url:
                Repository URL to copy.
            repo_path:
                Local path to store the repository copy.
        """
        Repo.clone_from(url, repo_path)

    def _update_repository(self, repo_path: Path) -> None:
        """Execute git pull on an existing repository.
        """
        Repo(repo_path).remotes.origin.pull()
    