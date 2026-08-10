from pathlib import Path
from datetime import datetime
import os
import time

import numpy as np
import sounddevice as sd
import soundfile as sf
import whisper


PROJECT_ROOT = Path(__file__).resolve().parent.parent

AUDIO_OUTPUT_DIR = (
    PROJECT_ROOT
    / "results"
    / "audio"
)


SAMPLE_RATE = 16000
CHANNELS = 1
DEFAULT_DURATION = 3.0
DEFAULT_MODEL = "tiny.en"

SILENCE_THRESHOLD = 0.001


_whisper_model = None


# ---------------------------------------------------------
# Microphone selection
# ---------------------------------------------------------

def get_microphone_device():
    """
    Resolve the microphone device.

    Priority:
    1. WATCHME_MIC_DEVICE environment override
    2. Operating system / SoundDevice default input

    Returns an integer device index.
    """

    device_override = os.getenv(
        "WATCHME_MIC_DEVICE"
    )

    # -------------------------------------------------
    # Optional explicit override
    # -------------------------------------------------

    if (
        device_override is not None
        and
        device_override.strip() != ""
    ):
        try:
            return int(
                device_override
            )

        except ValueError:
            raise ValueError(
                "WATCHME_MIC_DEVICE must "
                "contain a valid integer "
                "device number."
            )

    # -------------------------------------------------
    # System default microphone
    # -------------------------------------------------

    default_device = (
        sd.default.device
    )

    input_device = None

    # sounddevice 0.5.x can return an
    # _InputOutputPair object.
    if hasattr(
        default_device,
        "input"
    ):
        input_device = (
            default_device.input
        )

    # Some versions allow index access.
    elif hasattr(
        default_device,
        "__getitem__"
    ):
        try:
            input_device = (
                default_device[0]
            )

        except Exception:
            input_device = None

    # Older/simple configurations may already
    # provide one integer.
    elif isinstance(
        default_device,
        (int, float)
    ):
        input_device = (
            default_device
        )

    if input_device is None:
        raise RuntimeError(
            "Could not determine the "
            "system default microphone."
        )

    try:
        input_device = int(
            input_device
        )

    except (
        TypeError,
        ValueError
    ):
        raise RuntimeError(
            "The system default microphone "
            "did not return a valid device "
            "number."
        )

    if input_device < 0:
        raise RuntimeError(
            "No default microphone input "
            "device is currently configured."
        )

    return input_device


def describe_microphone(
    device
):
    """
    Return a readable description of the
    selected microphone.
    """

    try:
        info = sd.query_devices(
            device,
            "input"
        )

        return (
            f"{device} - "
            f"{info.get('name', 'Unknown device')}"
        )

    except Exception:
        return str(
            device
        )


def list_input_devices():
    """
    Print all available audio input devices.

    Useful when setting WATCHME_MIC_DEVICE.
    """

    devices = (
        sd.query_devices()
    )

    print()
    print(
        "Available input devices"
    )

    print(
        "-----------------------"
    )

    found_input = False

    for index, device in enumerate(
        devices
    ):
        max_input_channels = (
            device.get(
                "max_input_channels",
                0
            )
        )

        if max_input_channels > 0:
            found_input = True

            print(
                f"{index}: "
                f"{device.get('name', 'Unknown')} "
                f"(inputs: {max_input_channels})"
            )

    if not found_input:
        print(
            "No input devices were found."
        )


# ---------------------------------------------------------
# Whisper
# ---------------------------------------------------------

def get_whisper_model(
    model_name=DEFAULT_MODEL
):
    global _whisper_model

    if _whisper_model is None:
        print(
            "Loading Whisper model: "
            f"{model_name}"
        )

        _whisper_model = (
            whisper.load_model(
                model_name
            )
        )

    return _whisper_model


# ---------------------------------------------------------
# Audio recording
# ---------------------------------------------------------

def record_audio(
    duration=DEFAULT_DURATION
):
    microphone_device = (
        get_microphone_device()
    )

    microphone_description = (
        describe_microphone(
            microphone_device
        )
    )

    print(
        "Using microphone: "
        f"{microphone_description}"
    )

    print(
        "Get ready..."
    )

    time.sleep(
        0.5
    )

    print(
        "Speak now."
    )

    audio = sd.rec(
        int(
            duration
            *
            SAMPLE_RATE
        ),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="float32",
        device=microphone_device
    )

    sd.wait()

    print(
        "Recording complete."
    )

    return audio


# ---------------------------------------------------------
# Audio level
# ---------------------------------------------------------

def calculate_audio_level(
    audio
):
    return float(
        np.sqrt(
            np.mean(
                np.square(
                    audio
                )
            )
        )
    )


# ---------------------------------------------------------
# Save audio
# ---------------------------------------------------------

def save_audio(
    audio,
    label="speech"
):
    AUDIO_OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = (
        datetime.now().strftime(
            "%Y%m%d_%H%M%S_%f"
        )
    )

    output_path = (
        AUDIO_OUTPUT_DIR
        /
        f"{label}_{timestamp}.wav"
    )

    sf.write(
        str(
            output_path
        ),
        audio,
        SAMPLE_RATE
    )

    return output_path


# ---------------------------------------------------------
# Whisper transcription
# ---------------------------------------------------------

def transcribe_audio(
    audio
):
    model = (
        get_whisper_model()
    )

    flattened_audio = (
        audio.flatten()
    )

    result = model.transcribe(
        flattened_audio,
        fp16=False,
        language="en"
    )

    return (
        result.get(
            "text",
            ""
        )
        .strip()
        .lower()
    )


# ---------------------------------------------------------
# Complete speech input workflow
# ---------------------------------------------------------

def capture_speech(
    label="speech",
    duration=DEFAULT_DURATION
):
    try:
        audio = record_audio(
            duration=duration
        )

        audio_level = (
            calculate_audio_level(
                audio
            )
        )

        print(
            "Audio level: "
            f"{audio_level:.6f}"
        )

        audio_path = save_audio(
            audio,
            label=label
        )

        relative_audio_path = str(
            audio_path.relative_to(
                PROJECT_ROOT
            )
        )

        # -------------------------------------------------
        # Silence handling
        # -------------------------------------------------

        if (
            audio_level
            <
            SILENCE_THRESHOLD
        ):
            return {
                "status": "no_input",
                "transcription": "",
                "audio_path": (
                    relative_audio_path
                ),
                "audio_level": (
                    audio_level
                ),
                "reason": (
                    "The microphone recording "
                    "was nearly silent."
                )
            }

        # -------------------------------------------------
        # Whisper
        # -------------------------------------------------

        transcription = (
            transcribe_audio(
                audio
            )
        )

        if transcription == "":
            return {
                "status": "success",
                "transcription": "",
                "audio_path": (
                    relative_audio_path
                ),
                "audio_level": (
                    audio_level
                ),
                "reason": (
                    "Audio was detected, but "
                    "Whisper did not return text."
                )
            }

        return {
            "status": "success",
            "transcription": (
                transcription
            ),
            "audio_path": (
                relative_audio_path
            ),
            "audio_level": (
                audio_level
            ),
            "reason": (
                "Speech was recorded and "
                "transcribed successfully."
            )
        }

    except Exception as error:
        return {
            "status": "error",
            "transcription": "",
            "audio_path": None,
            "audio_level": 0.0,
            "reason": str(
                error
            )
        }


# ---------------------------------------------------------
# Command-line test
# ---------------------------------------------------------

def main():
    print(
        "watchMe Speech Input Test"
    )

    print(
        "-------------------------"
    )

    print()
    print(
        "1. Test speech input"
    )

    print(
        "2. List input devices"
    )

    choice = input(
        "\nSelection: "
    ).strip()

    if choice == "2":
        list_input_devices()
        return

    result = capture_speech(
        label="speech_test"
    )

    print()
    print(
        "Speech Result"
    )

    print(
        "-------------"
    )

    for key, value in (
        result.items()
    ):
        print(
            f"{key}: {value}"
        )


if __name__ == "__main__":
    main()