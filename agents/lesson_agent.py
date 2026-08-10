from lessons.cvc_lesson import run_cvc_lesson
from lessons.shapes_lesson import run_shapes_lesson


class LessonAgent:

    def __init__(self):
        self.name = "LessonAgent"

    def run(
        self,
        lesson_type,
        input_mode="typed",
        status_callback=None
    ):
        lesson_type = (
            lesson_type
            .strip()
            .lower()
        )

        input_mode = (
            input_mode
            .strip()
            .lower()
        )

        if input_mode not in [
            "typed",
            "microphone"
        ]:
            return {
                "agent": self.name,
                "status": "error",
                "reason": (
                    "Input mode must be "
                    "'typed' or 'microphone'."
                )
            }

        if lesson_type == "cvc":

            lesson_result = (
                run_cvc_lesson(
                    input_mode=input_mode,
                    status_callback=(
                        status_callback
                    )
                )
            )

        elif lesson_type == "shapes":

            lesson_result = (
                run_shapes_lesson(
                    input_mode=input_mode,
                    status_callback=(
                        status_callback
                    )
                )
            )

        else:
            return {
                "agent": self.name,
                "status": "error",
                "lesson_type": (
                    lesson_type
                ),
                "reason": (
                    "Unsupported lesson type."
                )
            }

        return {
            "agent": self.name,
            "status": "success",
            "lesson_type": lesson_type,
            "input_mode": input_mode,
            "lesson": lesson_result
        }


def main():

    agent = LessonAgent()

    print(
        "watchMe Lesson Agent"
    )

    print(
        "--------------------"
    )

    print(
        "\nAvailable lessons:"
    )

    print(
        "1. CVC"
    )

    print(
        "2. Shapes"
    )

    choice = input(
        "\nSelect lesson: "
    ).strip()

    if choice == "1":
        lesson_type = "cvc"

    elif choice == "2":
        lesson_type = "shapes"

    else:
        lesson_type = (
            choice.lower()
        )

    print(
        "\nInput method:"
    )

    print(
        "1. Typed"
    )

    print(
        "2. Microphone + Whisper"
    )

    input_choice = input(
        "\nSelect input method: "
    ).strip()

    if input_choice == "2":
        input_mode = "microphone"

    else:
        input_mode = "typed"

    result = agent.run(
        lesson_type,
        input_mode=input_mode
    )

    print(
        "\nLessonAgent Result"
    )

    print(
        "------------------"
    )

    print(
        result
    )


if __name__ == "__main__":
    main()