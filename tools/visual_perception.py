from pathlib import Path
import cv2
import time
import json
import mediapipe as mp


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}

CENTER_TOLERANCE_X = 0.20
CENTER_TOLERANCE_Y = 0.20
TOO_FAR_THRESHOLD = 0.08
TOO_CLOSE_THRESHOLD = 0.55


def validate_image(image_path):
    path = Path(image_path)

    if not path.exists():
        return False, "File does not exist."

    if not path.is_file():
        return False, "Input is not a file."

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return False, f"Unsupported image format: {path.suffix}"

    return True, "Valid image file."


def detect_faces(image):
    project_root = Path(__file__).resolve().parent.parent
    model_path = project_root / "models" / "face_landmarker.task"

    if not model_path.exists():
        raise FileNotFoundError(
            f"MediaPipe face landmarker model was not found at: {model_path}"
        )

    base_options = mp.tasks.BaseOptions(
        model_asset_path=str(model_path)
    )

    options = mp.tasks.vision.FaceLandmarkerOptions(
        base_options=base_options,
        running_mode=mp.tasks.vision.RunningMode.IMAGE,
        num_faces=5
    )

    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_image
    )

    with mp.tasks.vision.FaceLandmarker.create_from_options(options) as landmarker:
        result = landmarker.detect(mp_image)

    return result.face_landmarks


def build_face_box(face_landmarks, image_width, image_height):
    x_values = [landmark.x for landmark in face_landmarks]
    y_values = [landmark.y for landmark in face_landmarks]

    x_min = max(0, int(min(x_values) * image_width))
    x_max = min(image_width - 1, int(max(x_values) * image_width))
    y_min = max(0, int(min(y_values) * image_height))
    y_max = min(image_height - 1, int(max(y_values) * image_height))

    box_width = max(1, x_max - x_min)
    box_height = max(1, y_max - y_min)
    area = box_width * box_height

    center_x = x_min + box_width / 2
    center_y = y_min + box_height / 2

    return {
        "x_min": x_min,
        "y_min": y_min,
        "x_max": x_max,
        "y_max": y_max,
        "box_width": box_width,
        "box_height": box_height,
        "area": area,
        "center_x": center_x,
        "center_y": center_y
    }


def get_face_position(face_box, image_width, image_height):
    image_center_x = image_width / 2
    image_center_y = image_height / 2

    offset_x_ratio = (
        face_box["center_x"] - image_center_x
    ) / image_width

    offset_y_ratio = (
        face_box["center_y"] - image_center_y
    ) / image_height

    horizontal = "center"
    vertical = "center"

    if offset_x_ratio < -CENTER_TOLERANCE_X:
        horizontal = "left"
    elif offset_x_ratio > CENTER_TOLERANCE_X:
        horizontal = "right"

    if offset_y_ratio < -CENTER_TOLERANCE_Y:
        vertical = "up"
    elif offset_y_ratio > CENTER_TOLERANCE_Y:
        vertical = "down"

    if horizontal == "center" and vertical == "center":
        position = "center"
    elif horizontal == "center":
        position = vertical
    elif vertical == "center":
        position = horizontal
    else:
        position = f"{vertical}-{horizontal}"

    face_centered = (
        horizontal == "center"
        and vertical == "center"
    )

    return (
        position,
        face_centered,
        round(offset_x_ratio, 4),
        round(offset_y_ratio, 4)
    )


def get_readiness(face_count, face_centered, face_size_ratio):
    if face_count == 0:
        return "no_face"

    if face_count > 1:
        return "multiple_faces"

    if face_size_ratio < TOO_FAR_THRESHOLD:
        return "move_closer"

    if face_size_ratio > TOO_CLOSE_THRESHOLD:
        return "move_back"

    if not face_centered:
        return "reposition"

    return "ready"


def get_decision_reason(readiness):
    reasons = {
        "no_face":
            "No face was detected in the image.",

        "multiple_faces":
            "More than one face was detected. "
            "watchMe requires one learner at a time.",

        "move_closer":
            "The learner's face is visible but too small "
            "in the frame.",

        "move_back":
            "The learner's face is too large in the frame.",

        "reposition":
            "The learner's face is visible but is not "
            "centered in the frame.",

        "ready":
            "One face is visible, centered, and within "
            "the expected size range."
    }

    return reasons.get(
        readiness,
        "No decision reason was available."
    )


def get_action_message(readiness):
    actions = {
        "no_face":
            "Move into view of the camera.",

        "multiple_faces":
            "Please make sure only one learner is "
            "in front of the camera.",

        "move_closer":
            "Move closer to the camera.",

        "move_back":
            "Move farther away from the camera.",

        "reposition":
            "Move toward the center of the camera.",

        "ready":
            "You are ready to begin the speech exercise."
    }

    return actions.get(
        readiness,
        "Please adjust your position and try again."
    )


def annotate_faces(image, face_boxes, readiness):
    for box in face_boxes:
        cv2.rectangle(
            image,
            (box["x_min"], box["y_min"]),
            (box["x_max"], box["y_max"]),
            (0, 255, 0),
            2
        )

    label = f"Status: {readiness}"

    cv2.putText(
        image,
        label,
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2,
        cv2.LINE_AA
    )

    return image


def save_trace(
    image_path,
    perception,
    readiness,
    decision_reason,
    action_message,
    annotated_output,
    processing_ms
):
    project_root = Path(__file__).resolve().parent.parent

    trace_dir = project_root / "results" / "traces"
    trace_dir.mkdir(parents=True, exist_ok=True)

    input_name = Path(image_path).stem
    trace_path = trace_dir / f"{input_name}_trace.json"

    relative_annotated_output = annotated_output.relative_to(project_root)

    trace = {
        "input": {
            "image": str(Path(image_path).as_posix())
        },

        "perception": perception,

        "decision": {
            "state": readiness,
            "reason": decision_reason
        },

        "action": {
            "message": action_message,
            "annotated_output": relative_annotated_output.as_posix()
        },

        "performance": {
            "processing_ms": processing_ms
        }
    }

    with open(trace_path, "w", encoding="utf-8") as file:
        json.dump(trace, file, indent=4)

    return trace_path


def analyze_image(image_path):
    start_time = time.perf_counter()

    valid, message = validate_image(image_path)

    if not valid:
        return {
            "status": "error",
            "input_path": str(image_path),
            "reason": message
        }

    image = cv2.imread(str(image_path))

    if image is None:
        return {
            "status": "error",
            "input_path": str(image_path),
            "reason":
                "OpenCV could not read the image. "
                "The file may be corrupt."
        }

    image_height, image_width = image.shape[:2]
    image_area = image_width * image_height

    try:
        faces = detect_faces(image)

    except Exception as error:
        return {
            "status": "error",
            "input_path": str(image_path),
            "reason": f"Face detection failed: {error}"
        }

    face_count = len(faces)
    face_detected = face_count > 0

    face_boxes = []

    for face_landmarks in faces:
        box = build_face_box(
            face_landmarks,
            image_width,
            image_height
        )

        face_boxes.append(box)

    primary_face = None

    if face_boxes:
        primary_face = max(
            face_boxes,
            key=lambda box: box["area"]
        )

    if primary_face is not None:
        (
            face_position,
            face_centered,
            offset_x_ratio,
            offset_y_ratio
        ) = get_face_position(
            primary_face,
            image_width,
            image_height
        )

        face_size_ratio = round(
            primary_face["area"] / image_area,
            4
        )

    else:
        face_position = None
        face_centered = False
        offset_x_ratio = None
        offset_y_ratio = None
        face_size_ratio = None

    readiness = get_readiness(
        face_count,
        face_centered,
        face_size_ratio
        if face_size_ratio is not None
        else 0
    )

    decision_reason = get_decision_reason(readiness)
    action_message = get_action_message(readiness)

    annotated_image = annotate_faces(
        image.copy(),
        face_boxes,
        readiness
    )

    project_root = Path(__file__).resolve().parent.parent

    output_dir = project_root / "results" / "images"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = (
        output_dir
        / f"annotated_{Path(image_path).name}"
    )

    cv2.imwrite(
        str(output_path),
        annotated_image
    )

    processing_ms = round(
        (time.perf_counter() - start_time) * 1000,
        2
    )

    perception = {
        "face_detected": face_detected,
        "face_count": face_count,
        "face_centered": face_centered,
        "face_position": face_position,
        "face_size_ratio": face_size_ratio,
        "offset_x_ratio": offset_x_ratio,
        "offset_y_ratio": offset_y_ratio
    }

    trace_path = save_trace(
        image_path=image_path,
        perception=perception,
        readiness=readiness,
        decision_reason=decision_reason,
        action_message=action_message,
        annotated_output=output_path,
        processing_ms=processing_ms
    )

    relative_output_path = output_path.relative_to(project_root)
    relative_trace_path = trace_path.relative_to(project_root)

    return {
        "status": "success",
        "input_path": str(Path(image_path).as_posix()),
        "image_width": image_width,
        "image_height": image_height,
        "channels":
            image.shape[2]
            if len(image.shape) == 3
            else 1,

        "face_detected": face_detected,
        "face_count": face_count,
        "face_centered": face_centered,
        "face_position": face_position,
        "face_size_ratio": face_size_ratio,

        "readiness": readiness,
        "decision_reason": decision_reason,
        "action_message": action_message,

        "offset_x_ratio": offset_x_ratio,
        "offset_y_ratio": offset_y_ratio,

        "annotated_output": relative_output_path.as_posix(),
        "trace_output": relative_trace_path.as_posix(),

        "processing_ms": processing_ms,

        "face_boxes": face_boxes
    }


if __name__ == "__main__":
    test_path = input(
        "Enter an image path: "
    ).strip()

    result = analyze_image(test_path)

    print("\nVisual Perception Result")
    print("------------------------")

    for key, value in result.items():
        print(f"{key}: {value}")