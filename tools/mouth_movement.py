from pathlib import Path
import argparse
import cv2
import json
import time

from tools.mouth_analysis import analyze_mouth_landmarks
from tools.visual_perception import detect_faces


MOVEMENT_DELTA_THRESHOLD = 0.03
MIN_VALID_FRAMES = 5


def analyze_frame(image):
    image_height, image_width = image.shape[:2]

    faces = detect_faces(image)

    if len(faces) != 1:
        return {
            "valid": False,
            "face_count": len(faces),
            "mouth_open_ratio": None
        }

    mouth_result = analyze_mouth_landmarks(
        faces[0],
        image_width,
        image_height
    )

    return {
        "valid": mouth_result["mouth_visible"],
        "face_count": 1,
        "mouth_open_ratio": mouth_result["mouth_open_ratio"]
    }


def calculate_movement(ratios):
    if len(ratios) < MIN_VALID_FRAMES:
        return {
            "movement_detected": False,
            "movement_score": 0.0,
            "average_delta": None,
            "reason": "Not enough valid mouth frames were available."
        }

    deltas = []

    for index in range(1, len(ratios)):
        delta = abs(
            ratios[index]
            -
            ratios[index - 1]
        )

        deltas.append(delta)

    if not deltas:
        return {
            "movement_detected": False,
            "movement_score": 0.0,
            "average_delta": None,
            "reason": "No frame-to-frame mouth changes were available."
        }

    average_delta = sum(deltas) / len(deltas)
    max_delta = max(deltas)

    movement_detected = (
        max_delta
        >=
        MOVEMENT_DELTA_THRESHOLD
    )

    if movement_detected:
        reason = (
            "Frame-to-frame mouth changes exceeded "
            "the movement threshold."
        )
    else:
        reason = (
            "Mouth-open ratios stayed relatively "
            "stable across frames."
        )

    return {
        "movement_detected":
            movement_detected,

        "movement_score":
            round(max_delta, 4),

        "average_delta":
            round(average_delta, 4),

        "reason":
            reason
    }


def save_trace(
    source_name,
    ratios,
    valid_frames,
    total_frames,
    movement_result,
    processing_ms
):
    project_root = (
        Path(__file__)
        .resolve()
        .parent
        .parent
    )

    trace_dir = (
        project_root
        /
        "results"
        /
        "traces"
    )

    trace_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    source_stem = Path(
        source_name
    ).stem

    trace_path = (
        trace_dir
        /
        f"{source_stem}_movement_trace.json"
    )

    trace = {
        "input": {
            "source":
                str(
                    Path(
                        source_name
                    ).as_posix()
                )
        },

        "perception": {
            "total_frames_processed":
                total_frames,

            "valid_mouth_frames":
                valid_frames,

            "mouth_open_ratios":
                ratios
        },

        "decision": {
            "movement_detected":
                movement_result[
                    "movement_detected"
                ],

            "movement_score":
                movement_result[
                    "movement_score"
                ],

            "average_delta":
                movement_result.get(
                    "average_delta"
                ),

            "reason":
                movement_result[
                    "reason"
                ]
        },

        "performance": {
            "processing_ms":
                processing_ms
        }
    }

    with open(
        trace_path,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            trace,
            file,
            indent=4
        )

    return (
        trace_path
        .relative_to(
            project_root
        )
        .as_posix()
    )


def analyze_video(video_path):
    start_time = time.perf_counter()

    path = Path(video_path)

    if not path.exists():
        return {
            "status": "error",
            "reason": "Video file does not exist."
        }

    if not path.is_file():
        return {
            "status": "error",
            "reason": "Video input is not a file."
        }

    capture = cv2.VideoCapture(
        str(path)
    )

    if not capture.isOpened():
        return {
            "status": "error",
            "reason": "OpenCV could not open the video."
        }

    ratios = []
    total_frames = 0
    valid_frames = 0

    while True:
        success, frame = capture.read()

        if not success:
            break

        total_frames += 1

        try:
            frame_result = analyze_frame(
                frame
            )

        except Exception:
            continue

        if frame_result["valid"]:
            ratio = frame_result[
                "mouth_open_ratio"
            ]

            if ratio is not None:
                ratios.append(
                    ratio
                )

                valid_frames += 1

    capture.release()

    movement_result = calculate_movement(
        ratios
    )

    processing_ms = round(
        (
            time.perf_counter()
            -
            start_time
        )
        *
        1000,
        2
    )

    trace_output = save_trace(
        source_name=video_path,
        ratios=ratios,
        valid_frames=valid_frames,
        total_frames=total_frames,
        movement_result=movement_result,
        processing_ms=processing_ms
    )

    return {
        "status": "success",

        "input":
            path.as_posix(),

        "total_frames":
            total_frames,

        "valid_mouth_frames":
            valid_frames,

        "movement_detected":
            movement_result[
                "movement_detected"
            ],

        "movement_score":
            movement_result[
                "movement_score"
            ],

        "average_delta":
            movement_result.get(
                "average_delta"
            ),

        "reason":
            movement_result[
                "reason"
            ],

        "trace_output":
            trace_output,

        "processing_ms":
            processing_ms
    }


def analyze_camera():
    start_time = time.perf_counter()

    capture = cv2.VideoCapture(0)

    if not capture.isOpened():
        return {
            "status": "error",
            "reason": "Could not open the webcam."
        }

    print("watchMe camera test started.")
    print("Move your mouth naturally.")
    print("Press Q to stop.")

    ratios = []
    total_frames = 0
    valid_frames = 0

    while True:
        success, frame = capture.read()

        if not success:
            break

        total_frames += 1

        try:
            frame_result = analyze_frame(
                frame
            )

        except Exception:
            frame_result = {
                "valid": False,
                "mouth_open_ratio": None
            }

        if frame_result["valid"]:
            ratio = frame_result[
                "mouth_open_ratio"
            ]

            if ratio is not None:
                ratios.append(
                    ratio
                )

                valid_frames += 1

                cv2.putText(
                    frame,
                    f"Mouth ratio: {ratio}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2,
                    cv2.LINE_AA
                )

        cv2.imshow(
            "watchMe Mouth Movement",
            frame
        )

        if (
            cv2.waitKey(1)
            &
            0xFF
            ==
            ord("q")
        ):
            break

    capture.release()
    cv2.destroyAllWindows()

    movement_result = calculate_movement(
        ratios
    )

    processing_ms = round(
        (
            time.perf_counter()
            -
            start_time
        )
        *
        1000,
        2
    )

    trace_output = save_trace(
        source_name="camera_session",
        ratios=ratios,
        valid_frames=valid_frames,
        total_frames=total_frames,
        movement_result=movement_result,
        processing_ms=processing_ms
    )

    return {
        "status": "success",

        "input":
            "camera",

        "total_frames":
            total_frames,

        "valid_mouth_frames":
            valid_frames,

        "movement_detected":
            movement_result[
                "movement_detected"
            ],

        "movement_score":
            movement_result[
                "movement_score"
            ],

        "average_delta":
            movement_result.get(
                "average_delta"
            ),

        "reason":
            movement_result[
                "reason"
            ],

        "trace_output":
            trace_output,

        "processing_ms":
            processing_ms
    }


def print_result(result):
    print(
        "\nMouth Movement Result"
    )

    print(
        "---------------------"
    )

    for key, value in result.items():
        print(
            f"{key}: {value}"
        )


def main():
    parser = argparse.ArgumentParser(
        description=(
            "watchMe temporal mouth movement analysis"
        )
    )

    parser.add_argument(
        "--video",
        type=str,
        help="Path to a prerecorded video file."
    )

    parser.add_argument(
        "--camera",
        action="store_true",
        help="Use live webcam input."
    )

    args = parser.parse_args()

    if args.video:
        result = analyze_video(
            args.video
        )

    elif args.camera:
        result = analyze_camera()

    else:
        print(
            "Use --video <path> "
            "or --camera."
        )

        return

    print_result(
        result
    )


if __name__ == "__main__":
    main()
    