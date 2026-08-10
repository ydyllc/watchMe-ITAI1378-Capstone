from pathlib import Path
import cv2
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SAMPLE_DIR = PROJECT_ROOT / "data" / "sample"

SOURCE_IMAGE = SAMPLE_DIR / "oldmansmiling.jpg"


def main():
    image = cv2.imread(str(SOURCE_IMAGE))

    if image is None:
        print("Error: Could not load source image.")
        return

    # -------------------------------------------------
    # Dark image
    # -------------------------------------------------

    dark_image = cv2.convertScaleAbs(
        image,
        alpha=0.25,
        beta=0
    )

    cv2.imwrite(
        str(SAMPLE_DIR / "dark.jpg"),
        dark_image
    )

    # -------------------------------------------------
    # Blurry image
    # -------------------------------------------------

    blurry_image = cv2.GaussianBlur(
        image,
        (51, 51),
        0
    )

    cv2.imwrite(
        str(SAMPLE_DIR / "blurry.jpg"),
        blurry_image
    )

    # -------------------------------------------------
    # Blank image
    # -------------------------------------------------

    height, width = image.shape[:2]

    blank_image = np.zeros(
        (height, width, 3),
        dtype=np.uint8
    )

    cv2.imwrite(
        str(SAMPLE_DIR / "blank.jpg"),
        blank_image
    )

    # -------------------------------------------------
    # Corrupt image
    # -------------------------------------------------

    corrupt_path = SAMPLE_DIR / "corrupt.jpg"

    with open(
        corrupt_path,
        "wb"
    ) as file:
        file.write(
            b"This is intentionally not a valid JPEG file."
        )

    # -------------------------------------------------
    # Rotated left
    # -------------------------------------------------

    rotated_left = cv2.rotate(
        image,
        cv2.ROTATE_90_COUNTERCLOCKWISE
    )

    cv2.imwrite(
        str(SAMPLE_DIR / "rotated_left.jpg"),
        rotated_left
    )

    # -------------------------------------------------
    # Rotated right
    # -------------------------------------------------

    rotated_right = cv2.rotate(
        image,
        cv2.ROTATE_90_CLOCKWISE
    )

    cv2.imwrite(
        str(SAMPLE_DIR / "rotated_right.jpg"),
        rotated_right
    )

    # -------------------------------------------------
    # Upside down
    # -------------------------------------------------

    upside_down = cv2.rotate(
        image,
        cv2.ROTATE_180
    )

    cv2.imwrite(
        str(SAMPLE_DIR / "upside_down.jpg"),
        upside_down
    )

    # -------------------------------------------------
    # Black and white
    # -------------------------------------------------

    grayscale = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    black_white = cv2.cvtColor(
        grayscale,
        cv2.COLOR_GRAY2BGR
    )

    cv2.imwrite(
        str(SAMPLE_DIR / "black_white.jpg"),
        black_white
    )

    print("Robustness samples created:")
    print("data/sample/dark.jpg")
    print("data/sample/blurry.jpg")
    print("data/sample/blank.jpg")
    print("data/sample/corrupt.jpg")
    print("data/sample/rotated_left.jpg")
    print("data/sample/rotated_right.jpg")
    print("data/sample/upside_down.jpg")
    print("data/sample/black_white.jpg")


if __name__ == "__main__":
    main()