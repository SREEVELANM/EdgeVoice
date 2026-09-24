import os
from pydub import AudioSegment

# ============================================================
# EDGEVOICE AUDIO PREPROCESSOR
# ============================================================

RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"

TARGET_SAMPLE_RATE = 16000
TARGET_CHANNELS = 1
TARGET_SAMPLE_WIDTH = 2       # 16-bit PCM
TARGET_DURATION_MS = 1000     # 1 second

CLASSES = [
    "wake_word",
    "silence"
]

SUPPORTED_FORMATS = (
    ".wav",
    ".mp3",
    ".m4a",
    ".aac",
    ".ogg",
    ".flac"
)


def process_audio(input_path, output_path):

    # --------------------------------------------------------
    # Read audio using FFmpeg through pydub
    # --------------------------------------------------------

    audio = AudioSegment.from_file(input_path)

    # --------------------------------------------------------
    # Convert to:
    # Mono
    # 16 kHz
    # 16-bit PCM
    # --------------------------------------------------------

    audio = audio.set_channels(TARGET_CHANNELS)

    audio = audio.set_frame_rate(
        TARGET_SAMPLE_RATE
    )

    audio = audio.set_sample_width(
        TARGET_SAMPLE_WIDTH
    )

    # --------------------------------------------------------
    # Make exactly 1 second
    # --------------------------------------------------------

    if len(audio) < TARGET_DURATION_MS:

        # Pad the end with silence

        padding = AudioSegment.silent(
            duration=TARGET_DURATION_MS - len(audio),
            frame_rate=TARGET_SAMPLE_RATE
        )

        audio = audio + padding

    elif len(audio) > TARGET_DURATION_MS:

        # Keep first 1 second

        audio = audio[:TARGET_DURATION_MS]

    # --------------------------------------------------------
    # Export as WAV
    # --------------------------------------------------------

    os.makedirs(
        os.path.dirname(output_path),
        exist_ok=True
    )

    audio.export(
        output_path,
        format="wav",
        parameters=[
            "-ac", "1",
            "-ar", "16000",
            "-sample_fmt", "s16"
        ]
    )


def process_category(category):

    input_folder = os.path.join(
        RAW_DIR,
        category
    )

    output_folder = os.path.join(
        PROCESSED_DIR,
        category
    )

    if not os.path.exists(input_folder):

        print()
        print("ERROR: Folder not found:")
        print(input_folder)

        return 0, 0

    os.makedirs(
        output_folder,
        exist_ok=True
    )

    files = [
        file
        for file in os.listdir(input_folder)
        if file.lower().endswith(SUPPORTED_FORMATS)
    ]

    print()
    print("=" * 60)
    print(f"PROCESSING: {category.upper()}")
    print("=" * 60)

    print(f"Found files: {len(files)}")

    successful = 0
    failed = 0

    for index, filename in enumerate(files, start=1):

        input_path = os.path.join(
            input_folder,
            filename
        )

        output_filename = (
            f"{category}_{index:04d}.wav"
        )

        output_path = os.path.join(
            output_folder,
            output_filename
        )

        try:

            process_audio(
                input_path,
                output_path
            )

            successful += 1

            print(
                f"[{index}/{len(files)}] "
                f"OK: {filename} -> {output_filename}"
            )

        except Exception as error:

            failed += 1

            print(
                f"[{index}/{len(files)}] "
                f"FAILED: {filename}"
            )

            print(
                f"       Error: {error}"
            )

    print()
    print(f"Successful: {successful}")
    print(f"Failed:     {failed}")

    return successful, failed


def main():

    print()
    print("=" * 60)
    print("              EDGEVOICE")
    print("         AUDIO PREPROCESSOR")
    print("=" * 60)

    total_successful = 0
    total_failed = 0

    for category in CLASSES:

        successful, failed = process_category(
            category
        )

        total_successful += successful
        total_failed += failed

    print()
    print("=" * 60)
    print("          PREPROCESSING COMPLETE")
    print("=" * 60)

    print(
        f"Total successful : {total_successful}"
    )

    print(
        f"Total failed     : {total_failed}"
    )

    print()
    print("Audio specification:")
    print("Sample rate : 16000 Hz")
    print("Channels    : Mono")
    print("Duration    : 1 second")
    print("Format      : WAV")
    print("Bit depth   : 16-bit PCM")

    print()
    print("Output:")
    print(
        os.path.abspath(PROCESSED_DIR)
    )

    print()


if __name__ == "__main__":
    main()