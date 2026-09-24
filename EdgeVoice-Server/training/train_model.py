import os
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

# Suppress TensorFlow C++ logging warnings for a cleaner terminal
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

print("=" * 60)
print("EDGEVOICE - ROBUST CNN MODEL TRAINING")
print("=" * 60)

# ============================================================
# 1. LOAD DATA
# ============================================================
try:
    X = np.load("features/X_mfcc.npy")
    y = np.load("features/y.npy")
except FileNotFoundError:
    print("Error: Could not find feature files. Run extract_features.py first.")
    exit()

# CNNs require a channel dimension. 
# Reshape from (samples, 40, 101) to (samples, 40, 101, 1)
X = X[..., np.newaxis] 

print(f"Data shape for CNN: {X.shape}")

# ============================================================
# 2. SPLIT DATA
# ============================================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

# ============================================================
# 3. BUILD THE CNN ARCHITECTURE
# ============================================================
model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(40, 101, 1)),
    
    # --- DATA AUGMENTATION ---
    # Randomly shifts the audio left/right by up to 20% during training.
    # This prevents "alignment bias" so you don't have to perfectly 
    # time your wake word during live inference.
    tf.keras.layers.RandomTranslation(
        height_factor=0.0,       # Don't shift pitch/frequency
        width_factor=0.2,        # Shift time left/right by 20%
        fill_mode='constant'
    ),
    
    # First Convolutional Block
    tf.keras.layers.Conv2D(16, (3, 3), activation='relu'),
    tf.keras.layers.MaxPooling2D((2, 2)),
    
    # Second Convolutional Block
    tf.keras.layers.Conv2D(32, (3, 3), activation='relu'),
    tf.keras.layers.MaxPooling2D((2, 2)),
    
    # Flatten and Classify
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dropout(0.5), # Drops random neurons to prevent memorization
    tf.keras.layers.Dense(1, activation='sigmoid') # Outputs a probability
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# ============================================================
# 4. TRAIN THE MODEL
# ============================================================
print("\nTraining CNN with Data Augmentation...")
history = model.fit(
    X_train, y_train, 
    epochs=30,               # Increased slightly to accommodate augmented data
    batch_size=16, 
    validation_data=(X_test, y_test)
)

# ============================================================
# 5. TEST AND EVALUATE
# ============================================================
print("\nEvaluating...")
y_pred_probs = model.predict(X_test)
y_pred = (y_pred_probs > 0.5).astype(int).flatten()

print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=["silence/noise", "wake_word"]))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# ============================================================
# 6. SAVE MODEL
# ============================================================
os.makedirs("models", exist_ok=True)

# Save in the standard .h5 format that TFLite conversion expects later
model.save("models/edgevoice_cnn.h5")
print("\nModel saved successfully to models/edgevoice_cnn.h5")
print("=" * 60)