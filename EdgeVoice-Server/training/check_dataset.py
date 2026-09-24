import os
import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# EDGEVOICE - DATASET VALIDATION
# ============================================================

FEATURE_FILE = "features/X_mfcc.npy"
LABEL_FILE = "features/y.npy"

# ------------------------------------------------------------
# Load dataset
# ------------------------------------------------------------

X = np.load(FEATURE_FILE)
y = np.load(LABEL_FILE)

print()
print("=" * 60)
print("              EDGEVOICE")
print("          DATASET VALIDATION")
print("=" * 60)

print()
print("Dataset information")
print("-" * 60)

print(f"Feature shape : {X.shape}")
print(f"Label shape   : {y.shape}")
print(f"Total samples : {len(y)}")

# ------------------------------------------------------------
# Class counts
# ------------------------------------------------------------

wake_count = np.sum(y == 1)
silence_count = np.sum(y == 0)

print()
print("Class distribution")
print("-" * 60)

print(f"Wake word : {wake_count}")
print(f"Silence   : {silence_count}")

# ------------------------------------------------------------
# Check invalid values
# ------------------------------------------------------------

print()
print("Checking feature values...")
print("-" * 60)

nan_count = np.isnan(X).sum()
inf_count = np.isinf(X).sum()

print(f"NaN values       : {nan_count}")
print(f"Infinite values  : {inf_count}")

# ------------------------------------------------------------
# Check feature dimensions
# ------------------------------------------------------------

print()
print("Feature dimensions")
print("-" * 60)

print(f"MFCC coefficients : {X.shape[1]}")
print(f"Time frames       : {X.shape[2]}")

# ------------------------------------------------------------
# Statistics
# ------------------------------------------------------------

print()
print("Feature statistics")
print("-" * 60)

print(f"Minimum : {X.min():.4f}")
print(f"Maximum : {X.max():.4f}")
print(f"Mean    : {X.mean():.4f}")
print(f"Std     : {X.std():.4f}")

# ------------------------------------------------------------
# Dataset balance
# ------------------------------------------------------------

ratio = wake_count / silence_count

print()
print("Class balance")
print("-" * 60)

print(f"Wake/Silence ratio : {ratio:.2f}")

if 0.5 <= ratio <= 2.0:
    print("STATUS: Dataset balance is acceptable")
else:
    print("WARNING: Dataset is significantly imbalanced")

# ------------------------------------------------------------
# Overall validation
# ------------------------------------------------------------

print()
print("=" * 60)

if (
    len(y) > 0
    and X.shape[0] == y.shape[0]
    and X.shape[1] == 40
    and nan_count == 0
    and inf_count == 0
):

    print("DATASET STATUS: READY FOR TRAINING")

else:

    print("DATASET STATUS: PROBLEM FOUND")

print("=" * 60)

# ------------------------------------------------------------
# Visualize one wake-word sample
# ------------------------------------------------------------

wake_indices = np.where(y == 1)[0]
silence_indices = np.where(y == 0)[0]

if len(wake_indices) > 0:

    plt.figure(figsize=(10, 5))

    plt.imshow(
        X[wake_indices[0]],
        aspect="auto",
        origin="lower"
    )

    plt.title("Wake Word - MFCC")
    plt.xlabel("Time Frames")
    plt.ylabel("MFCC Coefficients")

    plt.colorbar(
        label="Normalized MFCC"
    )

    plt.tight_layout()

    os.makedirs("results", exist_ok=True)

    plt.savefig(
        "results/wake_word_mfcc.png",
        dpi=150
    )

    plt.show()

# ------------------------------------------------------------
# Visualize one silence sample
# ------------------------------------------------------------

if len(silence_indices) > 0:

    plt.figure(figsize=(10, 5))

    plt.imshow(
        X[silence_indices[0]],
        aspect="auto",
        origin="lower"
    )

    plt.title("Silence - MFCC")
    plt.xlabel("Time Frames")
    plt.ylabel("MFCC Coefficients")

    plt.colorbar(
        label="Normalized MFCC"
    )

    plt.tight_layout()

    plt.savefig(
        "results/silence_mfcc.png",
        dpi=150
    )

    plt.show()