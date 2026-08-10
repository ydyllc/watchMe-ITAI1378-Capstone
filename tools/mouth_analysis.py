from pathlib import Path
import cv2
import time

from tools.visual_perception import (
    validate_image,
    detect_faces
)


UPPER_INNER_LIP = 13
LOWER_INNER_LIP = 14
LEFT_MOUTH_CORNER = 61
RIGHT_MOUTH_CORNER = 291

MOUTH_OPEN_THRESHOLD = 0.08


def landmark_to_pixel(
    landmark,
    image_width,
    image_height
):
    x = int(landmark.x * image_width)
    y = int(landmark.y * image_height)

    return x, y


def point_distance(
    point_a,
    point_b
):
    x1, y1 = point_a
    x2, y2 = point_b

    return (
        (x2 - x1) ** 2
        +
        (y2 - y1) ** 2
    ) ** 0.5


def analyze_mouth_landmarks(
    face_landmarks,
    image_width,
    image_height
):
    upper_lip = landmark_to_pixel(
        face_landmarks[UPPER_INNER_LIP],
        image_width,
        image_height
    )

    lower_lip = landmark_to_pixel(
        face_landmarks[LOWER_INNER_LIP],
        image_width,
        image_height
    )

    left_corner = landmark_to_pixel(
        face_landmarks[LEFT_MOUTH_CORNER],
        image_width,
        image_height
    )

    right_corner = landmark_to_pixel(
        face_landmarks[RIGHT_MOUTH_CORNER],
        image_width,
        image_height
    )

    mouth_height = point_distance(
        upper_lip,
        lower_lip
    )

    mouth_width = point_distance(
        left_corner,
        right_corner
    )

    if mouth_width == 0:
        mouth_open_ratio = 0.0
    else:
        mouth_open_ratio = (
            mouth_height
            /
            mouth_width
        )

    mouth_open_ratio = round(
        mouth_open_ratio,
        4
    )

    mouth_open = (
        mouth_open_ratio
        >=
        MOUTH_OPEN_THRESHOLD
    )

    key_points = [
        upper_lip,
        lower_lip,
        left_corner,
        right_corner
    ]

    mouth_visible = all(
        0 <= x < image_width
        and
        0 <= y < image_height
        for x, y in key_points
    )

    x_values = [
        point[0]
        for point in key_points
    ]

    y_values = [
        point[1]
        for point in key_points
    ]

    mouth_box = {
        "x_min": min(x_values),
        "y_min": min(y_values),
        "x_max": max(x_values),
        "y_max": max(y_values)
    }

    return {
        "mouth_visible":
            mouth_visible,

        "mouth_open":
            mouth_open,

        "mouth_open_ratio":
            mouth_open_ratio,

        "mouth_height_pixels":
            round(
                mouth_height,
                2
            ),

        "mouth_width_pixels":
            round(
                mouth_width,
                2
            ),

        "mouth_box":
            mouth_box,

        "mouth_points": {
            "upper_lip":
                upper_lip,

            "lower_lip":
                lower_lip,

            "left_corner":
                left_corner,

            "right_corner":
                right_corner
        }
    }


def annotate_mouth(
    image,
    mouth_result
):
    box = mouth_result[
        "mouth_box"
    ]

    cv2.rectangle(
        image,
        (
            box["x_min"],
            box["y_min"]
        ),
        (
            box["x_max"],
            box["y_max"]
        ),
        (0, 255, 0),
        2
    )

    for point in mouth_result[
        "mouth_points"
    ].values():

        cv2.circle(
            image,
            point,
            3,
            (0, 255, 0),
            -1
        )

    mouth_state = (
        "open"
        if mouth_result[
            "mouth_open"
        ]
        else
        "closed"
    )

    label = (
        f"Mouth: {mouth_state} "
        f"ratio="
        f"{mouth_result['mouth_open_ratio']}"
    )

    cv2.putText(
        image,
        label,
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (0, 255, 0),
        2,
        cv2.LINE_AA
    )

    return image


def analyze_mouth(
    image_path
):
    start_time = time.perf_counter()

    valid, message = validate_image(
        image_path
    )

    if not valid:
        return {
            "status":
                "error",

            "input_path":
                str(image_path),

            "reason":
                message
        }

    image = cv2.imread(
        str(image_path)
    )

    if image is None:
        return {
            "status":
                "error",

            "input_path":
                str(image_path),

            "reason":
                "OpenCV could not read the image. "
                "The file may be corrupt."
        }

    image_height, image_width = (
        image.shape[:2]
    )

    try:
        faces = detect_faces(
            image
        )

    except Exception as error:
        return {
            "status":
                "error",

            "input_path":
                str(image_path),

            "reason":
                f"Face landmark detection failed: "
                f"{error}"
        }

    face_count = len(
        faces
    )

    if face_count == 0:
        return {
            "status":
                "success",

            "input_path":
                str(
                    Path(
                        image_path
                    ).as_posix()
                ),

            "face_count":
                0,

            "mouth_visible":
                False,

            "mouth_open":
                None,

            "mouth_open_ratio":
                None,

            "reason":
                "No face was detected, so the mouth "
                "could not be analyzed."
        }

    if face_count > 1:
        return {
            "status":
                "success",

            "input_path":
                str(
                    Path(
                        image_path
                    ).as_posix()
                ),

            "face_count":
                face_count,

            "mouth_visible":
                False,

            "mouth_open":
                None,

            "mouth_open_ratio":
                None,

            "reason":
                "Multiple faces were detected. "
                "Mouth analysis requires one learner."
        }

    mouth_result = (
        analyze_mouth_landmarks(
            faces[0],
            image_width,
            image_height
        )
    )

    annotated_image = (
        annotate_mouth(
            image.copy(),
            mouth_result
        )
    )

    project_root = (
        Path(__file__)
        .resolve()
        .parent
        .parent
    )

    output_dir = (
        project_root
        /
        "results"
        /
        "images"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = (
        output_dir
        /
        f"mouth_annotated_"
        f"{Path(image_path).name}"
    )

    cv2.imwrite(
        str(output_path),
        annotated_image
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

    relative_output = (
        output_path
        .relative_to(
            project_root
        )
    )

    return {
        "status":
            "success",

        "input_path":
            str(
                Path(
                    image_path
                ).as_posix()
            ),

        "face_count":
            face_count,

        "mouth_visible":
            mouth_result[
                "mouth_visible"
            ],

        "mouth_open":
            mouth_result[
                "mouth_open"
            ],

        "mouth_open_ratio":
            mouth_result[
                "mouth_open_ratio"
            ],

        "mouth_height_pixels":
            mouth_result[
                "mouth_height_pixels"
            ],

        "mouth_width_pixels":
            mouth_result[
                "mouth_width_pixels"
            ],

        "mouth_box":
            mouth_result[
                "mouth_box"
            ],

        "annotated_output":
            relative_output
            .as_posix(),

        "processing_ms":
            processing_ms
    }


if __name__ == "__main__":
    test_path = input(
        "Enter an image path: "
    ).strip()

    result = analyze_mouth(
        test_path
    )

    print(
        "\nMouth Analysis Result"
    )

    print(
        "---------------------"
    )

    for key, value in result.items():
        print(
            f"{key}: {value}"
        )