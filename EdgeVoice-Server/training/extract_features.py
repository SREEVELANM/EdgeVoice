import os
import numpy as np
import librosa

# ============================================================
# EDGEVOICE - MFCC FEATURE EXTRACTION
# ============================================================

PROCESSED_DIR = "data/processed"
FEATURE_DIR = "features"

SAMPLE_RATE = 16000

# MFCC configuration
N_MFCC = 40
N_FFT = 512
HOP_LENGTH = 160
MAX_TIME_STEPS = 101  # Enforced target length for the time dimension

CLASSES = {
    "wake_word": 1,
    "silence": 0
}


def extract_mfcc(file_path):

    # Load audio
    audio, sr = librosa.load(
        file_path,
        sr=SAMPLE_RATE,
        mono=True
    )

    # Extract MFCC
    mfcc = librosa.feature.mfcc(
        y=audio,
        sr=sr,
        n_mfcc=N_MFCC,
        n_fft=N_FFT,
        hop_length=HOP_LENGTH
    )

    # Ensure consistent shape (padding/truncating along the time axis)
    if mfcc.shape[1] > MAX_TIME_STEPS:
        # Truncate
        mfcc = mfcc[:, :MAX_TIME_STEPS]
    elif mfcc.shape[1] < MAX_TIME_STEPS:
        # Pad with zeros
        pad_width = MAX_TIME_STEPS - mfcc.shape[1]
        mfcc = np.pad(
            mfcc, 
            pad_width=((0, 0), (0, pad_width)), 
            mode='constant'
        )

    # Normalize each MFCC coefficient
    mfcc = (
        mfcc - np.mean(mfcc, axis=1, keepdims=True)
    ) / (
        np.std(mfcc, axis=1, keepdims=True) + 1e-8
    )

    return mfcc.astype(np.float32)


def process_class(class_name, label):

    input_dir = os.path.join(
        PROCESSED_DIR,
        class_name
    )

    features = []
    labels = []

    files = sorted([
        f for f in os.listdir(input_dir)
        if f.lower().endswith(".wav")
    ])

    print()
    print("=" * 60)
    print(f"CLASS: {class_name.upper()}")
    print("=" * 60)

    print(f"Files found: {len(files)}")

    for index, filename in enumerate(files, start=1):

        path = os.path.join(
            input_dir,
            filename
        )

        try:

            mfcc = extract_mfcc(path)

            features.append(mfcc)
            labels.append(label)

            print(
                f"[{index}/{len(files)}] OK: {filename} "
                f"Shape: {mfcc.shape}"
            )

        except Exception as error:

            print(
                f"[{index}/{len(files)}] FAILED: {filename}"
            )

            print(f"Error: {error}")

    return features, labels


def main():

    print()
    print("=" * 60)
    print("              EDGEVOICE")
    print("          MFCC EXTRACTION")
    print("=" * 60)

    all_features = []
    all_labels = []

    # Process both classes
    for class_name, label in CLASSES.items():

        features, labels = process_class(
            class_name,
            label
        )

        all_features.extend(features)
        all_labels.extend(labels)

    # Convert to NumPy arrays
    X = np.array(
        all_features,
        dtype=np.float32
    )

    y = np.array(
        all_labels,
        dtype=np.int64
    )

    # Create feature directory
    os.makedirs(
        FEATURE_DIR,
        exist_ok=True
    )

    # Save
    np.save(
        os.path.join(
            FEATURE_DIR,
            "X_mfcc.npy"
        ),
        X
    )

    np.save(
        os.path.join(
            FEATURE_DIR,
            "y.npy"
        ),
        y
    )

    print()
    print("=" * 60)
    print("          FEATURE EXTRACTION COMPLETE")
    print("=" * 60)

    print(f"X shape     : {X.shape}")
    print(f"y shape     : {y.shape}")

    print()
    print("Labels:")
    print("0 = silence")
    print("1 = wake_word")

    print()
    print("Saved:")
    print("features/X_mfcc.npy")
    print("features/y.npy")


if __name__ == "__main__":
    main()