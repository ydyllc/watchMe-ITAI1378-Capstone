from difflib import SequenceMatcher
import time

from tools.speech_input import capture_speech


SHAPES = [
    "circle",
    "square",
    "triangle"
]

NEAR_MATCH_THRESHOLD = 0.65
PROMPT_DISPLAY_SECONDS = 1.0


def send_status(
    status_callback,
    event,
    **data
):
    """
    Send live lesson updates to an optional
    interface such as LiveLessonOrchestrator.
    """

    if status_callback is None:
        return

    status_callback({
        "event": event,
        **data
    })


def get_response(
    prompt,
    input_mode="typed",
    status_callback=None,
    item_number=None,
    total_items=None
):
    """
    Collect either typed input or microphone
    speech for one Shapes lesson item.
    """

    # Tell the live interface which shape
    # the learner should say.
    send_status(
        status_callback,
        "prompt",
        prompt=prompt,
        item_number=item_number,
        total_items=total_items
    )

    if input_mode == "microphone":

        print(
            f"Say: {prompt}"
        )

        # Give the learner enough time to see
        # the prompt in the camera window before
        # microphone recording begins.
        time.sleep(
            PROMPT_DISPLAY_SECONDS
        )

        send_status(
            status_callback,
            "listening",
            prompt=prompt,
            item_number=item_number,
            total_items=total_items
        )

        speech_result = capture_speech(
            label=f"shape_{prompt}"
        )

        response = speech_result[
            "transcription"
        ]

        print(
            "Whisper heard: "
            f"{response if response else '[no speech]'}"
        )

        send_status(
            status_callback,
            "response",
            prompt=prompt,
            response=response,
            audio_level=speech_result[
                "audio_level"
            ],
            item_number=item_number,
            total_items=total_items
        )

        return {
            "response": response,
            "audio_path": speech_result[
                "audio_path"
            ],
            "audio_level": speech_result[
                "audio_level"
            ],
            "input_status": speech_result[
                "status"
            ],
            "reason": speech_result[
                "reason"
            ]
        }

    # -------------------------------------------------
    # Typed fallback
    # -------------------------------------------------

    send_status(
        status_callback,
        "waiting_for_typed_input",
        prompt=prompt,
        item_number=item_number,
        total_items=total_items
    )

    response = input(
        f"Type: {prompt}\nResponse: "
    ).strip().lower()

    send_status(
        status_callback,
        "response",
        prompt=prompt,
        response=response,
        audio_level=None,
        item_number=item_number,
        total_items=total_items
    )

    return {
        "response": response,
        "audio_path": None,
        "audio_level": None,
        "input_status": "success",
        "reason": "Typed input received."
    }


def normalize_response(
    response
):
    """
    Normalize Whisper or typed text into
    individual words for evaluation.
    """

    cleaned = response.lower()

    punctuation = [
        ".",
        ",",
        "!",
        "?",
        ";",
        ":"
    ]

    for mark in punctuation:
        cleaned = cleaned.replace(
            mark,
            " "
        )

    return cleaned.split()


def similarity_score(
    expected,
    candidate
):
    return SequenceMatcher(
        None,
        expected,
        candidate
    ).ratio()


def evaluate_response(
    expected,
    response
):
    """
    Classify one response as:

    CORRECT
    NEAR_MATCH
    INCORRECT
    NO_INPUT
    """

    words = normalize_response(
        response
    )

    if not words:
        return "NO_INPUT"

    # Correct even when Whisper adds other
    # words around the expected response.
    if expected in words:
        return "CORRECT"

    best_similarity = max(
        similarity_score(
            expected,
            word
        )
        for word in words
    )

    if (
        best_similarity
        >=
        NEAR_MATCH_THRESHOLD
    ):
        return "NEAR_MATCH"

    return "INCORRECT"


def run_shapes_lesson(
    input_mode="typed",
    status_callback=None
):
    """
    Run the complete Shapes lesson.

    The optional status_callback sends live
    prompt, listening, response, outcome, and
    completion events to the camera interface.
    """

    print(
        "\nShapes Lesson"
    )

    print(
        "-------------"
    )

    print(
        f"Input mode: {input_mode}"
    )

    results = []

    total_items = len(
        SHAPES
    )

    send_status(
        status_callback,
        "lesson_started",
        lesson_type="shapes",
        total_items=total_items
    )

    for index, shape in enumerate(
        SHAPES,
        start=1
    ):
        print(
            f"\nShape {index} "
            f"of {total_items}"
        )

        response_result = get_response(
            shape,
            input_mode=input_mode,
            status_callback=status_callback,
            item_number=index,
            total_items=total_items
        )

        response = response_result[
            "response"
        ]

        outcome = evaluate_response(
            shape,
            response
        )

        result = {
            "prompt": shape,
            "response": response,
            "outcome": outcome,
            "attempt": 1,
            "input_mode": input_mode,
            "audio_path": response_result[
                "audio_path"
            ],
            "audio_level": response_result[
                "audio_level"
            ]
        }

        results.append(
            result
        )

        print(
            f"Outcome: {outcome}"
        )

        send_status(
            status_callback,
            "outcome",
            prompt=shape,
            response=response,
            outcome=outcome,
            item_number=index,
            total_items=total_items
        )

        # Briefly show feedback before moving
        # to the next shape.
        time.sleep(
            0.8
        )

    correct_count = sum(
        1
        for result in results
        if result["outcome"] == "CORRECT"
    )

    near_match_count = sum(
        1
        for result in results
        if result["outcome"] == "NEAR_MATCH"
    )

    incorrect_count = sum(
        1
        for result in results
        if result["outcome"] == "INCORRECT"
    )

    no_input_count = sum(
        1
        for result in results
        if result["outcome"] == "NO_INPUT"
    )

    summary = {
        "lesson_type": "shapes",
        "input_mode": input_mode,
        "total_items": len(
            results
        ),
        "correct": correct_count,
        "near_match": near_match_count,
        "incorrect": incorrect_count,
        "no_input": no_input_count,
        "results": results
    }

    send_status(
        status_callback,
        "lesson_complete",
        lesson_type="shapes",
        summary=summary
    )

    return summary


def main():
    result = run_shapes_lesson()

    print(
        "\nShapes Lesson Summary"
    )

    print(
        "---------------------"
    )

    print(
        result
    )


if __name__ == "__main__":
    main()