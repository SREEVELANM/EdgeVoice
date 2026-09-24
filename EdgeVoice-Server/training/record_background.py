import os
import time
import sounddevice as sd
from scipy.io.wavfile import write


# ============================================================
# EDGEVOICE
# BACKGROUND / NO-WAKE DATASET RECORDER
# ============================================================

SAMPLE_RATE = 16000
DURATION = 1

OUTPUT_DIR = "data/raw/no_wake"

NUMBER_OF_SAMPLES = 200


# ============================================================
# CREATE DIRECTORY
# ============================================================

os.makedirs(OUTPUT_DIR, exist_ok=True)


print()
print("=" * 60)
print("                 EDGEVOICE")
print("       BACKGROUND NO-WAKE RECORDER")
print("=" * 60)

print()
print("This recorder will collect background sounds.")
print()
print("DO NOT SAY THE WAKE WORD.")
print()
print("You can:")
print("- stay silent")
print("- let the fan run")
print("- type on the keyboard")
print("- move around")
print("- talk normally")
print("- tap the table")
print("- create normal room noise")
print()
print("We want REAL background noise.")
print()

input("Press ENTER when ready...")


print()
print("Starting in 3 seconds...")

time.sleep(3)


# ============================================================
# RECORD
# ============================================================

for i in range(1, NUMBER_OF_SAMPLES + 1):

    print(
        f"[{i:03d}/{NUMBER_OF_SAMPLES}] "
        "Recording..."
    )

    audio = sd.rec(
        int(SAMPLE_RATE * DURATION),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16"
    )

    sd.wait()

    filename = os.path.join(
        OUTPUT_DIR,
        f"background_{i:03d}.wav"
    )

    write(
        filename,
        SAMPLE_RATE,
        audio
    )

    print(
        f"        Saved: {filename}"
    )

    time.sleep(0.15)


# ============================================================
# COMPLETE
# ============================================================

print()
print("=" * 60)
print("           BACKGROUND RECORDING COMPLETE")
print("=" * 60)

print()
print(f"Samples recorded: {NUMBER_OF_SAMPLES}")
print()
print("Location:")
print(OUTPUT_DIR)

print()
print("IMPORTANT:")
print("These recordings are NO_WAKE samples.")
print()