import numpy as np
import sounddevice as sd
import librosa
import tensorflow as tf
import os

# Suppress standard TensorFlow logging to keep the console clean
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

print("============================================================")
print("                 EDGEVOICE - LIVE INFERENCE")
print("============================================================")

print("\nLoading EdgeVoice CNN...")
# Load the trained CNN model
model = tf.keras.models.load_model("models/edgevoice_cnn.h5")

# Audio and Trigger Settings
SAMPLE_RATE = 16000
DURATION = 1                  # 1-second audio windows
THRESHOLD = 0.5              # Lowered for non-overlapping window testing
REQUIRED_CONSECUTIVE = 1      # Set to 1 for this desktop test

consecutive_detections = 0

def extract_live_mfcc(audio_data):
    """
    Matches the extraction logic from extract_features.py perfectly
    so the live data shape (40, 101) exactly matches the training data.
    """
    # Extract MFCC
    mfcc = librosa.feature.mfcc(y=audio_data, sr=SAMPLE_RATE, n_mfcc=40, n_fft=512, hop_length=160)
    
    # Ensure consistent shape (padding/truncating along the time axis to 101)
    if mfcc.shape[1] > 101:
        mfcc = mfcc[:, :101]
    elif mfcc.shape[1] < 101:
        pad_width = 101 - mfcc.shape[1]
        mfcc = np.pad(mfcc, pad_width=((0, 0), (0, pad_width)), mode='constant')
        
    # Normalize
    mfcc = (mfcc - np.mean(mfcc, axis=1, keepdims=True)) / (np.std(mfcc, axis=1, keepdims=True) + 1e-8)
    
    return mfcc.astype(np.float32)

print("\nMicrophone active. Listening for wake word...\n")

try:
    while True:
        # 1. Record 1 second of audio
        audio = sd.rec(int(SAMPLE_RATE * DURATION), samplerate=SAMPLE_RATE, channels=1, dtype='float32')
        sd.wait()
        audio = audio.flatten()
        
        # 2. Process into MFCCs
        mfcc = extract_live_mfcc(audio)
        
        # 3. Add batch and channel dimensions for the CNN: (1, 40, 101, 1)
        mfcc_input = mfcc[np.newaxis, ..., np.newaxis] 
        
        # 4. Predict
        probability = model.predict(mfcc_input, verbose=0)[0][0]
        
        # 5. Print the live score dynamically on the same line
        print(f"Listening... (Live score: {probability:.4f})    ", end="\r")
        
        # 6. Trigger Logic
        if probability > THRESHOLD:
            consecutive_detections += 1
        else:
            consecutive_detections = 0
            
        if consecutive_detections >= REQUIRED_CONSECUTIVE:
            print(f"\n\n*** WAKE EVENT TRIGGERED! (Confidence: {probability:.2f}) ***\n")
            
            # Reset after a successful trigger
            consecutive_detections = 0 
            
except KeyboardInterrupt:
    print("\n\nStopped listening.")