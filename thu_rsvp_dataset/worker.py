from pathlib import Path
from typing import Callable, Optional

import numpy as np
from scipy.io import loadmat


def load_trials_one_session(
    mat_file: Path,
    channels_to_use: np.ndarray,
    original_sample_rate_hz: int,
    trial_duration_samples: int,
    transform: Optional[Callable] = None,
):
    """
    Worker function for multiprocess data loading.
    Each session is stored in a mat file. It consists of 2 blocks of 40 sequences.
    """
    trial_data, trial_labels = [], []
    contents = loadmat(mat_file)

    # Remove channels with indices 32 and 42.
    # E.g. try `np.arange(64)[np.r_[0:32,33:42,43:64]]`
    data1 = contents["EEGdata1"][channels_to_use].astype(np.float32)
    data2 = contents["EEGdata2"][channels_to_use].astype(np.float32)
    if transform is not None:
        data1, final_sample_rate_hz = transform(data1, original_sample_rate_hz)
        data2, final_sample_rate_hz = transform(data2, original_sample_rate_hz)
    else:
        final_sample_rate_hz = original_sample_rate_hz

    trial_onsets1 = contents["trigger_positions"][0]
    trial_onsets2 = contents["trigger_positions"][1]

    # Originally, "1" == target, "2" == non-target.
    # Subtract 1 to convert from "1" and "2" to "0" == target and "1" == non-target.
    labels1 = contents["class_labels"][0] - 1
    labels2 = contents["class_labels"][1] - 1

    # Hz * duration in s = duration in samples
    downsample_factor = original_sample_rate_hz / final_sample_rate_hz
    for data, trial_onsets, labels in [(data1, trial_onsets1, labels1), (data2, trial_onsets2, labels2)]:
        for i, trial_onset in enumerate(trial_onsets):
            # NOTE - after downsampling, need to convert sample indices
            converted_onset = int(trial_onset // downsample_factor)
            trial_data.append(data[..., converted_onset : converted_onset + trial_duration_samples])
            trial_labels.append(labels[i])
    return trial_data, trial_labels
