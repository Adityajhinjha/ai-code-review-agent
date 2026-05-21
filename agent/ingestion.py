import os
import stat
import shutil
from git import Repo
from urllib.parse import urlparse

CLONE_DIR = "tmp/cloned_repo"

IGNORE_DIRS = {
    ".git", "venv", "__pycache__",
    "node_modules", "dist", "build", ".venv", ".tox"
}


def _force_remove_readonly(func, path, _):
    """Error handler for shutil.rmtree to handle read-only files on Windows."""
    os.chmod(path, stat.S_IWRITE)
    func(path)


def validate_github_url(repo_url: str) -> bool:
    """Validate if the provided URL is a valid GitHub repository URL."""
    parsed = urlparse(repo_url)
    parts = parsed.path.strip("/").split("/")

    return (
        parsed.scheme in ["http", "https"]
        and "github.com" in parsed.netloc
        and len(parts) >= 2
        and all(parts[:2])
    )


def clone_repository(repo_url: str) -> str:
    """
    Clone the GitHub repository into a fixed temp folder.
    Wipes any previous clone before cloning.
    Returns the local repository path.
    """
    if not validate_github_url(repo_url):
        raise ValueError(f"Invalid GitHub repository URL: {repo_url}")

    # Wipe previous clone — using error handler for Windows read-only files
    if os.path.exists(CLONE_DIR):
        shutil.rmtree(CLONE_DIR, onerror=_force_remove_readonly)

    os.makedirs(CLONE_DIR, exist_ok=True)

    try:
        print(f"Cloning {repo_url} ...")
        Repo.clone_from(repo_url, CLONE_DIR)
        print("Repository cloned successfully.")
    except Exception as e:
        shutil.rmtree(CLONE_DIR, ignore_errors=True)
        raise RuntimeError(f"Clone failed: {e}")

    return CLONE_DIR


def get_python_files(repo_path: str) -> list[str]:
    """
    Recursively scan repository and return all Python files,
    skipping ignored directories and empty files.
    """
    python_files = []

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for file in files:
            if not file.endswith(".py"):
                continue

            full_path = os.path.join(root, file)

            if os.path.getsize(full_path) == 0:
                continue

            python_files.append(full_path)

    return python_files
