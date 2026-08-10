from pathlib import Path
import json
import time

from tools.visual_perception import analyze_image
from tools.mouth_analysis import analyze_mouth


class PerceptionAgent:
    """
    watchMe Perception Agent

    Combines the project's computer vision tools
    into one structured perception message for
    the reasoning layer.
    """

    def __init__(self):
        self.agent_name = "PerceptionAgent"

    def perceive(self, image_path):
        """
        Analyze one image using the available
        watchMe computer vision tools.

        Returns one structured perception message.
        """

        start_time = time.perf_counter()

        image_path = Path(image_path)

        # -------------------------------------------------
        # Tool 1: General visual perception
        # -------------------------------------------------

        visual_result = analyze_image(
            str(image_path)
        )

        if visual_result.get("status") != "success":
            return {
                "agent": self.agent_name,
                "status": "error",
                "input": image_path.as_posix(),
                "reason": visual_result.get(
                    "reason",
                    "Visual perception failed."
                )
            }

        # -------------------------------------------------
        # Decide whether mouth analysis is appropriate
        # -------------------------------------------------

        face_count = visual_result.get(
            "face_count",
            0
        )

        mouth_result = None

        if face_count == 1:
            mouth_result = analyze_mouth(
                str(image_path)
            )

        # -------------------------------------------------
        # Build structured face perception
        # -------------------------------------------------

        face_perception = {
            "detected": visual_result.get(
                "face_detected"
            ),
            "count": visual_result.get(
                "face_count"
            ),
            "centered": visual_result.get(
                "face_centered"
            ),
            "position": visual_result.get(
                "face_position"
            ),
            "size_ratio": visual_result.get(
                "face_size_ratio"
            ),
            "offset_x_ratio": visual_result.get(
                "offset_x_ratio"
            ),
            "offset_y_ratio": visual_result.get(
                "offset_y_ratio"
            ),
            "boxes": visual_result.get(
                "face_boxes",
                []
            )
        }

        # -------------------------------------------------
        # Build structured mouth perception
        # -------------------------------------------------

        if (
            mouth_result
            and
            mouth_result.get("status") == "success"
        ):
            mouth_perception = {
                "analyzed": True,
                "visible": mouth_result.get(
                    "mouth_visible"
                ),
                "open": mouth_result.get(
                    "mouth_open"
                ),
                "open_ratio": mouth_result.get(
                    "mouth_open_ratio"
                )
            }

        else:
            mouth_perception = {
                "analyzed": False,
                "visible": False,
                "open": None,
                "open_ratio": None
            }

        # -------------------------------------------------
        # Perception readiness
        # -------------------------------------------------

        readiness = visual_result.get(
            "readiness"
        )

        perception_ready = (
            readiness == "ready"
            and
            mouth_perception["analyzed"]
            and
            mouth_perception["visible"]
        )

        # -------------------------------------------------
        # Performance
        # -------------------------------------------------

        processing_ms = round(
            (
                time.perf_counter()
                - start_time
            )
            * 1000,
            2
        )

        # -------------------------------------------------
        # Final structured perception message
        # -------------------------------------------------

        perception_message = {
            "agent": self.agent_name,

            "status": "success",

            "input": {
                "image": image_path.as_posix()
            },

            "face": face_perception,

            "mouth": mouth_perception,

            "visual_readiness": readiness,

            "perception_ready": perception_ready,

            "artifacts": {
                "face_annotation":
                    visual_result.get(
                        "annotated_output"
                    ),

                "mouth_annotation":
                    (
                        mouth_result.get(
                            "annotated_output"
                        )
                        if mouth_result
                        else None
                    )
            },

            "performance": {
                "processing_ms": processing_ms
            }
        }

        return perception_message


def print_message(message):
    print(
        json.dumps(
            message,
            indent=4
        )
    )


def main():
    print(
        "\nwatchMe Perception Agent"
    )

    print(
        "------------------------"
    )

    image_path = input(
        "Enter an image path: "
    ).strip()

    agent = PerceptionAgent()

    result = agent.perceive(
        image_path
    )

    print(
        "\nPerception Message"
    )

    print(
        "------------------"
    )

    print_message(
        result
    )


if __name__ == "__main__":
    main()