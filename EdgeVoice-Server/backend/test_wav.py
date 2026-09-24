import os
import numpy as np
import librosa
import joblib


# ============================================================
# EDGEVOICE
# TEST WAKE WORD MODEL
# ============================================================

MODEL_PATH = "models/edgevoice_model.pkl"
SCALER_PATH = "models/edgevoice_scaler.pkl"

TEST_DIR = "data/test/wake_word_wav"

SAMPLE_RATE = 16000
DURATION = 1
TARGET_LENGTH = SAMPLE_RATE * DURATION


# ============================================================
# LOAD MODEL
# ============================================================

print()
print("Loading model...")

model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

print("Model loaded successfully.")


# ============================================================
# EXTRACT FEATURES
# MUST MATCH train_model.py
# ============================================================

def extract_features(filename):

    # Load audio

    audio, sr = librosa.load(
        filename,
        sr=SAMPLE_RATE,
        mono=True
    )


    # --------------------------------------------------------
    # FORCE AUDIO TO EXACTLY 1 SECOND
    # --------------------------------------------------------

    if len(audio) > TARGET_LENGTH:

        audio = audio[:TARGET_LENGTH]

    elif len(audio) < TARGET_LENGTH:

        audio = np.pad(
            audio,
            (
                0,
                TARGET_LENGTH - len(audio)
            )
        )


    # --------------------------------------------------------
    # EXTRACT MFCC
    # --------------------------------------------------------

    mfcc = librosa.feature.mfcc(
        y=audio,
        sr=SAMPLE_RATE,
        n_mfcc=40,
        n_fft=512,
        hop_length=160
    )


    # --------------------------------------------------------
    # CREATE 160 FEATURES
    # --------------------------------------------------------

    mfcc_mean = np.mean(
        mfcc,
        axis=1
    )

    mfcc_std = np.std(
        mfcc,
        axis=1
    )

    mfcc_min = np.min(
        mfcc,
        axis=1
    )

    mfcc_max = np.max(
        mfcc,
        axis=1
    )


    features = np.concatenate(
        [
            mfcc_mean,
            mfcc_std,
            mfcc_min,
            mfcc_max
        ]
    )


    # Convert to 2D

    features = features.reshape(
        1,
        -1
    )


    # Apply same scaler

    features = scaler.transform(
        features
    )


    return features


# ============================================================
# CHECK TEST FOLDER
# ============================================================

if not os.path.exists(TEST_DIR):

    print()
    print("ERROR: Test folder not found:")
    print(TEST_DIR)

    exit()


files = [
    f for f in os.listdir(TEST_DIR)
    if f.lower().endswith(".wav")
]


if len(files) == 0:

    print()
    print("NO WAV FILES FOUND")
    print()
    print("Put your test WAV files inside:")
    print(TEST_DIR)

    exit()


# ============================================================
# TEST FILES
# ============================================================

print()
print("=" * 60)
print("EDGEVOICE")
print("UNSEEN WAKE WORD TEST")
print("=" * 60)

print()


for filename in files:

    filepath = os.path.join(
        TEST_DIR,
        filename
    )


    try:

        features = extract_features(
            filepath
        )


        # Get probability

        probabilities = model.predict_proba(
            features
        )[0]


        wake_probability = probabilities[1]


        # Prediction using 0.5 threshold

        if wake_probability >= 0.5:

            prediction = "WAKE_WORD"

        else:

            prediction = "NO_WAKE"


        print(
            f"{filename:<20} "
            f"wake={wake_probability:.3f} "
            f"prediction={prediction}"
        )


    except Exception as e:

        print()
        print(f"ERROR testing {filename}")
        print(e)


print()
print("=" * 60)
print("TEST COMPLETE")
print("=" * 60)