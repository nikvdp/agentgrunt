import shutil
import httpx as requests
from pathlib import Path
import os
import tempfile
import tarfile
from tqdm import tqdm
from typing import Tuple, List


def move_directory(src_dir: Path, dest_dir: Path):
    dest_dir.mkdir(
        parents=True, exist_ok=True
    )  # Ensures that the destination directory exists
    shutil.move(str(src_dir), str(dest_dir))
    return dest_dir


def download_file(url: str, dest_path: Path):
    response = requests.get(url)
    with open(dest_path, "wb") as f:
        f.write(response.content)
    os.chmod(dest_path, 0o755)


def create_tarball(dir_to_tar: Path, tar_file_path: Path) -> Path:
    with tarfile.open(tar_file_path, "w:gz") as tar:
        for root, dirs, files in os.walk(dir_to_tar):
            for file in tqdm(
                files, desc=f"Compressing {dir_to_tar.name}", ncols=80, unit="file"
            ):
                absolute_file_path = os.path.join(root, file)
                relative_file_path = os.path.relpath(absolute_file_path, dir_to_tar)
                tar.add(absolute_file_path, arcname=relative_file_path)
    return tar_file_path


def move_file(src_file: Path, dest_dir: Path) -> Path:
    destination = dest_dir / src_file.name
    shutil.move(str(src_file), str(destination))
    return destination
