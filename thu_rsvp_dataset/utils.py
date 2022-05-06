import hashlib
from pathlib import Path
from typing import Iterable

import requests
from tqdm import tqdm

DEFAULT_CHUNKSIZE = 10 * 1024 * 1024


def download_url(url: str, output_filepath: Path) -> None:
    basename = url.split("/")[-1]
    with requests.get(url, stream=True) as r, open(output_filepath, "wb") as f:
        r.raise_for_status()
        total_size_in_bytes = int(r.headers.get("content-length", 0))
        chunk_size = 1024 * 1024 * 10
        gb_size = total_size_in_bytes / 1024 / 1024 / 1024
        desc = f"{basename} ({gb_size:.2f} GB)"
        with tqdm(
            total=total_size_in_bytes,
            desc=desc,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            position=1,
            leave=False,
        ) as pbar:
            for chunk in r.iter_content(chunk_size=chunk_size):
                pbar.update(len(chunk))
                f.write(chunk)


def file_sha256hash(filepath: Path, chunksize=DEFAULT_CHUNKSIZE) -> str:
    """Compute SHA256 hash for one file"""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(chunksize), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def verify_file(file: Path, sha256sum: str, verify_sha256=True, chunksize=DEFAULT_CHUNKSIZE) -> bool:
    if not file.exists():
        return False
    if not verify_sha256:
        return True
    return file_sha256hash(file, chunksize) == sha256sum


def folder_sha256sum(folder: Path, include_filenames=None, chunksize=DEFAULT_CHUNKSIZE) -> str:
    """
    Recursively compute sha256 checksum for a folder.
    If a list of filenames is provided, only those files will be included in the checksum.
    """
    sha256 = hashlib.sha256()
    for p in sorted(folder.rglob("**/*")):
        if p.is_file() and (include_filenames is None or p.name in include_filenames):
            with open(p, "rb") as f:
                for chunk in iter(lambda: f.read(chunksize), b""):
                    sha256.update(chunk)
    return sha256.hexdigest()


def verify_folder(
    folder: Path, expected_sha256sum: str, verify_sha256=True, include_filenames=None, chunksize=DEFAULT_CHUNKSIZE
) -> bool:
    """
    Recursively compute sha256 checksum for a folder.
    If a list of filenames is provided, only those files will be included in the checksum
    """
    if not folder.exists():
        return False

    if not verify_sha256:
        return True

    observed_sha256sum = folder_sha256sum(folder, include_filenames, chunksize)
    return observed_sha256sum == expected_sha256sum


def chunks(seq: Iterable, size: int):
    return (seq[pos : pos + size] for pos in range(0, len(seq), size))
