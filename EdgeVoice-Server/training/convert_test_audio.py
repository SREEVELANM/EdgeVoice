import os
from pydub import AudioSegment

# ============================================================
# EDGEVOICE
# TEST AUDIO CONVERTER
# M4A / MP3 → WAV
# ============================================================

INPUT_DIR = "data/test/wake_word"
OUTPUT_DIR = "data/test/wake_word_wav"

SAMPLE_RATE = 16000


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

os.makedirs(OUTPUT_DIR, exist_ok=True)

print()
print("=" * 60)
print("                 EDGEVOICE")
print("             TEST AUDIO CONVERTER")
print("=" * 60)
print()


# ============================================================
# FIND AUDIO FILES
# ============================================================

files = [
    f for f in os.listdir(INPUT_DIR)
    if f.lower().endswith(
        (".m4a", ".mp3", ".wav")
    )
]

print(f"Found files: {len(files)}")
print()


# ============================================================
# CONVERT
# ============================================================

success = 0
failed = 0

for i, filename in enumerate(files, 1):

    input_path = os.path.join(
        INPUT_DIR,
        filename
    )

    output_name = os.path.splitext(filename)[0] + ".wav"

    output_path = os.path.join(
        OUTPUT_DIR,
        output_name
    )

    try:
        # Load the audio file (PyDub automatically detects m4a/mp3)
        audio = AudioSegment.from_file(input_path)

        # Convert to target sample rate and Mono (1 channel)
        audio = audio.set_frame_rate(SAMPLE_RATE).set_channels(1)

        # Export as WAV (PyDub defaults to 16-bit PCM for WAV)
        audio.export(output_path, format="wav")

        print(
            f"[{i}/{len(files)}] OK: "
            f"{filename} -> {output_name}"
        )

        success += 1

    except Exception as e:

        print(
            f"[{i}/{len(files)}] FAILED: "
            f"{filename}"
        )

        print(f"    Error: {e}")

        failed += 1


# ============================================================
# COMPLETE
# ============================================================

print()
print("=" * 60)
print("              CONVERSION COMPLETE")
print("=" * 60)

print()
print(f"Successful : {success}")
print(f"Failed     : {failed}")

print()
print("Output:")
print(OUTPUT_DIR)
print()