from pathlib import Path
from urllib.parse import urlparse
from git import Repo

class RepositoryCloner:
    base_path: Path

    def __init__(self, base_path: str = "data/repos"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def get_repository(self, url: str, update: bool = True) -> Path:
        """
        Return a local copy of the repository. 
        Clone it if it doesn't exist. Otherwise get the current local copy or update it if required.
        """
        repo_name = self._validate_repository(url)
        repo_path = self.base_path / repo_name

        if not repo_path.exists():
            self._clone_repository(url, repo_path)

        elif update:
            self._update_repository(repo_path)

        return repo_path

    def _validate_repository(self, url: str) -> str:
        """
        Validate the repository URL and return the repository name.
        """
        url = urlparse(url)

        if url.netloc != "github.com":
            raise ValueError("Only GitHub repositories are supported.")

        repo_name = Path(url.path).stem

        if not repo_name:
            raise ValueError("Invalid repository URL.")

        return repo_name

    def _clone_repository(self, url: str, repo_path: Path) -> None:
        """
        Clone the repository and return the local path.
        """
        Repo.clone_from(url, repo_path)

    def _update_repository(self, repo_path: Path) -> None:
        """
        Execute git pull on an existing repository.
        """
        Repo(repo_path).remotes.origin.pull()
    