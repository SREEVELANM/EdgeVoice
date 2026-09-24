import numpy as np
import joblib
from sklearn.metrics import confusion_matrix, classification_report


print()
print("=" * 60)
print("                 EDGEVOICE")
print("              MODEL DIAGNOSTIC")
print("=" * 60)


# ============================================================
# LOAD DATA
# ============================================================

X = np.load("features/X_mfcc.npy")
y = np.load("features/y.npy")

model = joblib.load("models/edgevoice_model.pkl")
scaler = joblib.load("models/edgevoice_scaler.pkl")


print()
print("Dataset shape:", X.shape)
print()


# ============================================================
# CLASS DISTRIBUTION
# ============================================================

silence_count = np.sum(y == 0)
wake_count = np.sum(y == 1)

print("Class distribution")
print("-" * 60)

print(f"NO_WAKE / silence : {silence_count}")
print(f"WAKE_WORD         : {wake_count}")


# ============================================================
# FLATTEN
# ============================================================

X_flat = X.reshape(X.shape[0], -1)


# ============================================================
# SCALE
# ============================================================

X_scaled = scaler.transform(X_flat)


# ============================================================
# PREDICT TRAINING DATA
# ============================================================

probabilities = model.predict_proba(X_scaled)

wake_probabilities = probabilities[:, 1]

predictions = model.predict(X_scaled)


# ============================================================
# CONFUSION MATRIX
# ============================================================

print()
print("TRAINING DATA RESULTS")
print("-" * 60)

print()
print("Confusion Matrix:")

print(
    confusion_matrix(
        y,
        predictions
    )
)


print()
print("Classification Report:")

print(
    classification_report(
        y,
        predictions,
        target_names=[
            "NO_WAKE",
            "WAKE_WORD"
        ]
    )
)


# ============================================================
# PROBABILITY ANALYSIS
# ============================================================

print()
print("WAKE PROBABILITY ANALYSIS")
print("-" * 60)


print()
print("Actual NO_WAKE samples:")

no_wake_probs = wake_probabilities[y == 0]

print(
    "Min :",
    round(float(np.min(no_wake_probs)), 4)
)

print(
    "Mean:",
    round(float(np.mean(no_wake_probs)), 4)
)

print(
    "Max :",
    round(float(np.max(no_wake_probs)), 4)
)


print()
print("Actual WAKE_WORD samples:")

wake_probs = wake_probabilities[y == 1]

print(
    "Min :",
    round(float(np.min(wake_probs)), 4)
)

print(
    "Mean:",
    round(float(np.mean(wake_probs)), 4)
)

print(
    "Max :",
    round(float(np.max(wake_probs)), 4)
)


# ============================================================
# LOWEST WAKE TRAINING SAMPLES
# ============================================================

print()
print("LOWEST CONFIDENCE WAKE SAMPLES")
print("-" * 60)

wake_indices = np.where(y == 1)[0]

sorted_wake = sorted(
    zip(
        wake_indices,
        wake_probs
    ),
    key=lambda x: x[1]
)

for index, probability in sorted_wake[:10]:

    print(
        f"Sample index={index:4d} "
        f"wake_probability={probability:.4f}"
    )


# ============================================================
# HIGHEST FALSE POSITIVE SAMPLES
# ============================================================

print()
print("HIGHEST NO_WAKE CONFIDENCE")
print("-" * 60)

no_wake_indices = np.where(y == 0)[0]

sorted_no_wake = sorted(
    zip(
        no_wake_indices,
        no_wake_probs
    ),
    key=lambda x: x[1],
    reverse=True
)

for index, probability in sorted_no_wake[:10]:

    print(
        f"Sample index={index:4d} "
        f"wake_probability={probability:.4f}"
    )


print()
print("=" * 60)
print("              DIAGNOSTIC COMPLETE")
print("=" * 60)