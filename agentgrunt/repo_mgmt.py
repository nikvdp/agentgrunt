import os
import tarfile
import tempfile
from pathlib import Path
from typing import Union
from urllib.parse import urlparse

from plumbum.cmd import git
from tqdm import tqdm


def is_github_url(value: str) -> bool:
    if Path(value).exists() and Path(value).is_dir():
        return False
    parsed = urlparse(value)
    if parsed.netloc == "github.com" and parsed.scheme in ["http", "https"]:
        return True
    # Check for shorthand notation
    elif "/" in value and not parsed.scheme and not parsed.netloc:
        return True
    return False


def valid_git_repo(value: str) -> str:
    if (
        Path(value).exists()
        and Path(value).is_dir()
        and (Path(value) / ".git").is_dir()
    ):
        return value
    elif is_github_url(str(value)):
        if "github.com" not in str(value):
            # Convert shorthand to full URL
            value = f"https://github.com/{value}"
        return value
    else:
        raise ValueError(
            f"'{value}' is neither an existing directory nor a valid GitHub URL."
        )


def get_clone_url(val: str) -> str:
    """
    Returns the URL to clone the repo.
    """
    if Path(val).exists() and Path(val).is_dir():
        # file:// makes --depth work on local clones
        return f"file://{Path(val).resolve()}"
    elif is_github_url(val):
        if "github.com" not in val:
            return f"https://github.com/{val}.git"
        else:
            return f"{val}.git"
    else:
        raise ValueError(f"'{val}' is not a valid GitHub URL.")


def clone_git_repo_to_temp_dir(git_repo: str, shallow: bool = True) -> Path:
    is_local = True
    if is_github_url(git_repo):
        # Clone the repo to a temporary directory
        local_repo = Path(tempfile.mkdtemp())
        is_local = False
    else:
        local_repo = Path(git_repo)

        # Ensure the directory exists and contains a .git folder
        if not local_repo.exists() or not local_repo.is_dir():
            raise ValueError(f"'{local_repo}' is not a valid directory.")
        if not (local_repo / ".git").exists():
            raise ValueError(f"'{local_repo}' does not contain a .git folder.")

    # Create a temporary directory
    temp_dir = Path(tempfile.mkdtemp())

    # Clone the git repo to the temporary directory
    clone_command = ["clone"]
    if shallow:
        clone_command.extend(["--depth", "5"])  # TODO: make this configurable
        if is_local:
            checked_out_branch = git["rev-parse", "--abbrev-ref", "HEAD"](
                cwd=local_repo.resolve()
            ).strip()
            if checked_out_branch:
                clone_command.extend(["--branch", checked_out_branch])

    clone_command.extend(
        [
            get_clone_url(git_repo),
            str(temp_dir),
        ]
    )
    git[clone_command]()
    git["gc"](cwd=temp_dir)

    return temp_dir


def tar_directory(path_to_directory: Path, compression="gz") -> Path:
    # Ensure the directory exists
    if not path_to_directory.exists() or not path_to_directory.is_dir():
        raise ValueError(f"'{path_to_directory}' is not a valid directory.")

    # Validate compression type
    if compression not in ["gz", "bz2"]:
        raise ValueError(
            f"Invalid compression type: {compression}. Choose from 'gz' or 'bz2'."
        )

    # Create a temporary tar file
    tar_file = tempfile.mktemp(suffix=f".tar.{compression}")

    # Get the total number of files to compress for progress reporting
    total_files = sum(len(files) for _, _, files in os.walk(path_to_directory))

    with tarfile.open(tar_file, f"w:{compression}") as tar:
        with tqdm(
            total=total_files, desc=f"Compressing {path_to_directory.name}"
        ) as pbar:
            for root, dirs, files in os.walk(path_to_directory):
                for file in files:
                    absolute_file_path = os.path.join(root, file)
                    relative_file_path = os.path.relpath(
                        absolute_file_path, path_to_directory
                    )
                    tar.add(absolute_file_path, arcname=relative_file_path)
                    pbar.update()

    return Path(tar_file)
