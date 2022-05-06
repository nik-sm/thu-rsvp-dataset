from pathlib import Path

from thu_rsvp_dataset import THU_RSVP_Dataset, get_default_transform

# Specify location to store files (or location of previously downloaded files)
datasets_dir = Path(__file__).resolve().parent.parent / "datasets"
datasets_dir.mkdir(exist_ok=True, parents=True)

# (Optional) Construct a transformation to apply to each file during loading
# This must be a callable of the following signature:
#
#     def transform(data: np.ndarray, original_sample_rate_hz: int) ->  Tuple(np.ndarray, int):
#         ...
#         return transformed_data, new_sample_rate_hz
#
transform = get_default_transform(
    sample_rate_hz=250,  # Sample rate of original dataset
    notch_freq_hz=50,  # AC line frequency in China
    notch_quality_factor=30,
    bandpass_low=2,  # Low frequency cutoff
    bandpass_high=45,  # High frequency cutoff
    bandpass_order=5,  # Order of Butterworth filter
    downsample_factor=2,  # Downsample by 2
)

# Load dataset
thu_rsvp = THU_RSVP_Dataset(
    dir=datasets_dir,
    trial_duration_ms=500,
    transform=transform,
    download=True,
    verify_sha256=False,
    verbose=True,
    force_extract=False,  # NOTE - set this to true after changing transforms
)
data, labels = thu_rsvp.get_data()

print(data.shape, labels.shape)
