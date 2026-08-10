import cv2


def test_camera(index, backend=None):
    if backend is None:
        capture = cv2.VideoCapture(index)
        backend_name = "DEFAULT"
    else:
        capture = cv2.VideoCapture(index, backend)
        backend_name = str(backend)

    print(
        f"Camera {index} | Backend {backend_name} | "
        f"Opened: {capture.isOpened()}"
    )

    if capture.isOpened():
        success, frame = capture.read()

        print(
            f"Frame read: {success}"
        )

        if success and frame is not None:
            print(
                f"Frame size: {frame.shape}"
            )

    capture.release()


def main():
    print("Testing default backend")

    for index in range(4):
        test_camera(index)

    print("\nTesting Windows DirectShow")

    for index in range(4):
        test_camera(
            index,
            cv2.CAP_DSHOW
        )

    print("\nTesting Windows Media Foundation")

    for index in range(4):
        test_camera(
            index,
            cv2.CAP_MSMF
        )


if __name__ == "__main__":
    main()