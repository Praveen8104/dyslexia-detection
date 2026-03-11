import numpy as np
import librosa

NUM_MFCC = 13
MAX_FRAMES = 200
# Total features: 13 MFCC + 13 delta + 13 delta-delta = 39
NUM_FEATURES = 39


def extract_mfcc_features(signal: np.ndarray, sr: int = 16000) -> np.ndarray:
    """Extract MFCC + delta + delta-delta features with normalization.

    Returns: numpy array of shape (MAX_FRAMES, 39)
      - 13 MFCCs + 13 delta + 13 delta-delta = 39 features
      - Padded/truncated to MAX_FRAMES (200) frames
      - Per-feature standardized (zero mean, unit variance)
    """
    # Extract MFCCs
    mfccs = librosa.feature.mfcc(y=signal, sr=sr, n_mfcc=NUM_MFCC)

    # Compute deltas
    delta = librosa.feature.delta(mfccs)
    delta2 = librosa.feature.delta(mfccs, order=2)

    # Stack: shape = (39, num_frames)
    features = np.vstack([mfccs, delta, delta2])

    # Transpose to (num_frames, 39)
    features = features.T

    # Per-feature standardization (zero mean, unit variance)
    mean = np.mean(features, axis=0, keepdims=True)
    std = np.std(features, axis=0, keepdims=True) + 1e-8
    features = (features - mean) / std

    # Pad or truncate to MAX_FRAMES
    if features.shape[0] < MAX_FRAMES:
        pad_width = MAX_FRAMES - features.shape[0]
        features = np.pad(features, ((0, pad_width), (0, 0)), mode="constant")
    else:
        features = features[:MAX_FRAMES]

    return features.astype(np.float32)
