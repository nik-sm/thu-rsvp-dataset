import multiprocessing
import subprocess
from functools import partial
from multiprocessing import Pool
from pathlib import Path
from typing import Callable, Optional, Tuple

import numpy as np
from loguru import logger
from tqdm import tqdm

from .files import (
    ALL_FILES_AND_SHA256SUMS,
    SOURCE_URL,
    WHICH_FOLDER_EACH_SUBJECT,
    ZIP_FILES_AND_SHA256SUMS,
)
from .utils import download_url, file_sha256hash, verify_file
from .worker import load_trials_one_session


class THU_RSVP_Dataset:
    def __init__(
        self,
        dir: Path,
        trial_duration_ms: int,
        transform: Optional[Callable] = None,
        download=False,
        verify_sha256=True,
        verbose=False,
        force_extract=False,
    ):
        """
        Wrapper class for loading THU RSVP Dataset.
        Contains 1,024,000 trials (64 subjects * 2 sessions * 2 blocks * 40 sequences * 100 trials per sequence)
        See https://www.frontiersin.org/articles/10.3389/fnins.2020.568000/full for details.

        Args:
            dir (Path): path to store downloaded and extracted files
            trial_duration_ms (int): desired duration of each trial in milliseconds after stimulus onset
            transform (Optional[Callable]): transform function to apply to each session.
                Transform must take data and original sample rate, and return transformed data and new sample rate.
            download (bool): whether to download original files. Defaults to False.
            verify_sha256 (bool): whether to verify sha256 checksums of downloaded files. Defaults to True.
            verbose (bool): whether to print verbose info. Defaults to False.
            force_extract (bool): if True, ignores previously saved *.npy results and re-extracts.
                NOTE - Use this to re-process after changing transform functions.
        """
        self.dir = dir / "thu"
        self.trial_duration_ms = trial_duration_ms
        self.transform = transform
        self.download = download
        self.verbose = verbose
        self.verify_sha256 = verify_sha256
        self.n_trials = 64 * 2 * 2 * 40 * 100
        self.original_sample_rate_hz = 250
        # Remove channels with indices 32 and 42, based on guidance in pper
        self.channels_to_use = np.r_[0:32, 33:42, 43:64]
        self.n_channels = len(self.channels_to_use)
        self.force_extract = force_extract

        if self.transform is not None:
            # Create dummy data and check what shape transform produces
            dummy_duration = int(self.trial_duration_ms / 1000 * self.original_sample_rate_hz)
            dummy_data = np.ones((self.n_channels, dummy_duration))
            dummy_output, self.final_sample_rate_hz = transform(dummy_data, self.original_sample_rate_hz)
            self.output_shape = dummy_output.shape
        else:
            self.final_sample_rate_hz = self.original_sample_rate_hz
            self.output_shape = (self.n_channels, int(self.trial_duration_ms / 1000 * self.final_sample_rate_hz))
        self.trial_duration_samples = self.output_shape[-1]

    def get_data(self):
        if self.verbose:
            logger.info("Check download...")
        self._check_download()
        if self.verbose:
            logger.info("Decompress...")
        self._decompress()
        if self.verbose:
            logger.info("Extract trials...")
        self.data, self.labels = self._extract_trials()
        return self.data, self.labels

    def _check_download(self) -> None:
        if self.download:
            self.dir.mkdir(exist_ok=True, parents=True)

        for basename, md5_hash in tqdm(ALL_FILES_AND_SHA256SUMS, desc="Download + Verify Files", leave=True):
            output_path = self.dir / basename
            if verify_file(output_path, md5_hash, verify_sha256=self.verify_sha256):
                if self.verbose:
                    logger.info(f"Already have {str(output_path)}, verified checksum: {self.verify_sha256} ")
                continue

            if self.download:  # Download if necessary
                download_url(SOURCE_URL + "/" + basename, output_path)

            if not verify_file(output_path, md5_hash, self.verify_sha256):  # Verify download
                raise ValueError(f"md5sum mismatch for: {basename}")

    def _decompress(self, force=False) -> None:
        for zip_file, _ in tqdm(ZIP_FILES_AND_SHA256SUMS, desc="Decompress", leave=True):
            inpath = self.dir / zip_file
            outpath = self.dir / zip_file[:-4]  # Remove ".zip"

            if not force and outpath.exists():
                if self.verbose:
                    logger.info(f"Skipping {str(outpath)}")
                continue
            else:
                if self.verbose:
                    logger.info(f"Decompressing {inpath} to {outpath}")
                subprocess.run(f"unzip -o -q {str(inpath)} -d {str(outpath)}", shell=True, check=True)

    def _extract_trials(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        NOTE - File layout is as follows

            self.dir/
                S1-S10.mat/
                    sub1A.mat    # Each subject has an A and B session
                    sub1B.mat
                    sub2A.mat
                    sub2B.mat
                    ...
                S11-20.mat/
                    ...
                ...
                S61-64.mat/
                    ...

        File contents using `loadmat(".../subj1A.mat").items()`:
            {
                "EEGdata1": ...,           # First block of 40 stimulus sequences, shape (64, T1)
                "EEGdata2": ...,           # Second block of 40 stimulus sequences. shape (64, T2)
                "trigger_positions": ...,  # Trigger positions for each sequence. shape (2, 4000)
                                           #   First row from first block, second from second block.
                "class_labels": ...,       # Class labels for each sequence. shape (2, 4000)
                                           #   First row from first block, second from second block.
            }

        Data in EEGdata1 and EEGdata2 are 250 Hz data (downsampled from raw 1000 Hz device):

            From paper text, it is clear that stimuli appear at 10 Hz, so we can compare timestamps after 100 triggers.
            For one sequence, trigger0 = 6829. trigger99 = 9304.
            9304 - 6829 = 2475 samples long to cover 99 intervals of 100ms
            2475 samples / (99 * 0.1 s) = 250 Hz
        """
        trial_data_path = self.dir / f"trial_data.{self.trial_duration_ms}ms.npy"
        trial_data_sha256_path = self.dir / f"trial_data.{self.trial_duration_ms}ms.sha256"
        trial_labels_path = self.dir / f"trial_labels.{self.trial_duration_ms}ms.npy"
        trial_labels_sha256_path = self.dir / f"trial_labels.{self.trial_duration_ms}ms.sha256"

        def can_reuse():
            if not trial_data_sha256_path.exists() or not trial_labels_sha256_path.exists():
                if self.verbose:
                    logger.info("Cannot reuse trial data, because one or more files are missing.")
                return False
            if not verify_file(trial_data_path, trial_data_sha256_path.read_text(), verify_sha256=self.verify_sha256):
                if self.verbose:
                    logger.info("Cannot reuse trial data, because data file checksum fails.")
                return False
            if not verify_file(
                trial_labels_path, trial_labels_sha256_path.read_text(), verify_sha256=self.verify_sha256
            ):
                if self.verbose:
                    logger.info("Cannot reuse trial data, because label file checksum fails.")
                return False
            return True

        if not self.force_extract and can_reuse():  # Try to use pre-existing files if possible
            if self.verbose:
                logger.info(f"Loading previously extracted data and labels. verified checksum: {self.verify_sha256}.")
            return np.load(trial_data_path), np.load(trial_labels_path)

        mat_files = [
            self.dir / WHICH_FOLDER_EACH_SUBJECT[subj_idx] / f"sub{subj_idx}{session}.mat"
            for subj_idx in range(1, 65)
            for session in ["A", "B"]
        ]

        # Assign trials and labels directly into arrays to avoid memory overhead.
        data = np.empty(shape=(self.n_trials, *self.output_shape), dtype=np.float32)
        labels = np.empty(shape=(self.n_trials,), dtype=int)

        n_processes = int(multiprocessing.cpu_count() / 2 * 3)  # All processes reading *.mat files - probably IO bound
        with Pool(n_processes) as pool:
            worker_fn = partial(
                load_trials_one_session,
                channels_to_use=self.channels_to_use,
                original_sample_rate_hz=self.original_sample_rate_hz,
                trial_duration_samples=self.trial_duration_samples,
                transform=self.transform,
            )
            cursor = 0
            for subject_trial_data, subject_trial_labels in tqdm(
                # use imap to get partial results as they become available (trying to avoid memory overhead)
                pool.imap(worker_fn, mat_files, chunksize=1),
                desc="Extract Trials",
                total=len(mat_files),
                leave=True,
            ):
                data[cursor : cursor + len(subject_trial_data)] = subject_trial_data
                labels[cursor : cursor + len(subject_trial_labels)] = subject_trial_labels
                cursor += len(subject_trial_data)

        # Save data and SHA256 checksum
        if self.verbose:
            logger.info(f"Saving {trial_data_path}")
        np.save(trial_data_path, data)
        if self.verbose:
            logger.info(f"Saving {trial_data_sha256_path}")
        trial_data_sha256_path.write_text(file_sha256hash(trial_data_path))

        # Save labels and SHA256 checksum
        if self.verbose:
            logger.info(f"Saving {trial_labels_path}")
        np.save(trial_labels_path, labels)
        if self.verbose:
            logger.info(f"Saving {trial_labels_sha256_path}")
        trial_labels_sha256_path.write_text(file_sha256hash(trial_labels_path))
        return data, labels
