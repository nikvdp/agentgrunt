import os
import tarfile
import tempfile
from pathlib import Path

from plumbum.cmd import git
from tqdm import tqdm


def clone_git_repo_to_temp_dir(path_to_git_repo: Path, shallow: bool = True) -> Path:
    # Ensure the directory exists and contains a .git folder
    if not path_to_git_repo.exists() or not path_to_git_repo.is_dir():
        raise ValueError(f"'{path_to_git_repo}' is not a valid directory.")
    if not (path_to_git_repo / ".git").exists():
        raise ValueError(f"'{path_to_git_repo}' does not contain a .git folder.")

    # Create a temporary directory
    temp_dir = Path(tempfile.mkdtemp())

    # Clone the git repo to the temporary directory
    clone_command = ["clone"]
    if shallow:
        clone_command.extend(["--depth", "5"])  # TODO: make this configurable
        checked_out_branch = git["rev-parse", "--abbrev-ref", "HEAD"](
            cwd=path_to_git_repo.resolve()
        ).strip()
        if checked_out_branch:
            clone_command.extend(["--branch", checked_out_branch])

    clone_command.extend(
        [
            # file:// makes --depth work on local clones
            "file://" + str(path_to_git_repo.resolve()),
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
