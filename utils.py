import shutil
import httpx
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

    for item in src_dir.iterdir():
        shutil.move(str(item), str(dest_dir))

    return dest_dir


def download_file(url: str, dest_path: Path) -> Path:
    with httpx.stream("GET", url, follow_redirects=True) as response:
        total_size = int(response.headers.get("content-length", 0))
        block_size = 1024  # 1 Kibibyte
        t = tqdm(
            desc="Downloading git binary",
            total=total_size,
            unit="iB",
            unit_scale=True,
            ncols=80,
        )

        with open(dest_path, "wb") as f:
            for chunk in response.iter_bytes(chunk_size=block_size):
                t.update(len(chunk))
                f.write(chunk)
        t.close()

        if total_size != 0 and t.n != total_size:
            raise Exception("ERROR, something went wrong with the download")

    return dest_path


def create_tarball(dir_to_tar: Path, tar_file_path: Path, compression="gz") -> Path:
    # Ensure the directory exists
    if not dir_to_tar.exists() or not dir_to_tar.is_dir():
        raise ValueError(f"'{dir_to_tar}' is not a valid directory.")

    # Validate compression type
    if compression not in ["gz", "bz2"]:
        raise ValueError(
            f"Invalid compression type: {compression}. Choose from 'gz' or 'bz2'."
        )

    # Get the total number of files to compress for progress reporting
    total_files = sum(len(files) for _, _, files in os.walk(dir_to_tar))

    with tarfile.open(tar_file_path, f"w:{compression}") as tar:
        with tqdm(
            total=total_files,
            desc=f"Compressing source dir",
            ncols=80,
            unit="file",
        ) as pbar:
            for root, dirs, files in os.walk(dir_to_tar):
                for file in files:
                    absolute_file_path = os.path.join(root, file)
                    relative_file_path = os.path.relpath(absolute_file_path, dir_to_tar)
                    tar.add(absolute_file_path, arcname=relative_file_path)
                    pbar.update()

    return tar_file_path


def move_file(src_file: Path, dest_dir: Path) -> Path:
    destination = dest_dir / src_file.name
    shutil.move(str(src_file), str(destination))
    return destination
