import json


class PlannerAgent:
    """
    watchMe Planner Agent

    Consumes structured output from the PerceptionAgent
    and decides what the system should do next.

    Every response follows the same structured schema:
    agent -> status -> decision -> action
    """

    def __init__(self):
        self.agent_name = "PlannerAgent"


    def plan(self, perception_message):
        # -------------------------------------------------
        # Rule 0: Perception error
        # -------------------------------------------------

        if perception_message.get("status") != "success":
            return self._decision(
                state="STOP",
                reason=perception_message.get(
                    "reason",
                    "Perception failed."
                ),
                action=(
                    "Stop processing this input and "
                    "report the perception error."
                ),
                status="error"
            )


        face = perception_message.get(
            "face",
            {}
        )

        mouth = perception_message.get(
            "mouth",
            {}
        )

        face_count = face.get(
            "count",
            0
        )

        face_centered = face.get(
            "centered",
            False
        )

        face_position = face.get(
            "position",
            "unknown"
        )

        visual_readiness = perception_message.get(
            "visual_readiness"
        )

        mouth_analyzed = mouth.get(
            "analyzed",
            False
        )

        mouth_visible = mouth.get(
            "visible",
            False
        )


        # -------------------------------------------------
        # Rule 1: No learner visible
        # -------------------------------------------------

        if face_count == 0:
            return self._decision(
                state="WAIT_FOR_USER",
                reason=(
                    "No learner face was detected."
                ),
                action=(
                    "Move into view of the camera."
                )
            )


        # -------------------------------------------------
        # Rule 2: Multiple learners visible
        # -------------------------------------------------

        if face_count > 1:
            return self._decision(
                state="ONE_LEARNER_REQUIRED",
                reason=(
                    "More than one face was detected."
                ),
                action=(
                    "Make sure only one learner is "
                    "in front of the camera."
                )
            )


        # -------------------------------------------------
        # Rule 3: Learner is off center
        # -------------------------------------------------

        if not face_centered:
            return self._decision(
                state="REPOSITION",
                reason=(
                    f"The learner's face is visible "
                    f"but is positioned {face_position} "
                    f"of the acceptable center area."
                ),
                action=(
                    "Move toward the center of the camera."
                )
            )


        # -------------------------------------------------
        # Rule 4: Learner is too far away
        # -------------------------------------------------

        if visual_readiness == "move_closer":
            return self._decision(
                state="MOVE_CLOSER",
                reason=(
                    "The learner is centered, but the "
                    "face is too small in the frame."
                ),
                action=(
                    "Move closer to the camera."
                )
            )


        # -------------------------------------------------
        # Rule 5: Learner is too close
        # -------------------------------------------------

        if visual_readiness == "move_back":
            return self._decision(
                state="MOVE_BACK",
                reason=(
                    "The learner is centered, but the "
                    "face is too large in the frame."
                ),
                action=(
                    "Move farther away from the camera."
                )
            )


        # -------------------------------------------------
        # Rule 6: Mouth analysis unavailable
        # -------------------------------------------------

        if not mouth_analyzed:
            return self._decision(
                state="CHECK_MOUTH",
                reason=(
                    "Face readiness passed but mouth "
                    "analysis was not completed."
                ),
                action=(
                    "Retry mouth analysis before "
                    "starting the exercise."
                )
            )


        # -------------------------------------------------
        # Rule 7: Mouth not visible
        # -------------------------------------------------

        if not mouth_visible:
            return self._decision(
                state="MOUTH_NOT_VISIBLE",
                reason=(
                    "The learner's face is ready but "
                    "the mouth is not clearly visible."
                ),
                action=(
                    "Adjust position so the mouth "
                    "is visible."
                )
            )


        # -------------------------------------------------
        # Rule 8: Ready
        # -------------------------------------------------

        return self._decision(
            state="READY",
            reason=(
                "One learner is visible, properly "
                "positioned, and the mouth is visible."
            ),
            action=(
                "Begin the speech practice exercise."
            )
        )


    def _decision(
        self,
        state,
        reason,
        action,
        status="success"
    ):
        return {
            "agent": self.agent_name,

            "status": status,

            "decision": {
                "state": state,
                "reason": reason
            },

            "action": {
                "message": action
            }
        }


def print_message(message):
    print(
        json.dumps(
            message,
            indent=4
        )
    )


def main():
    print(
        "PlannerAgent is designed to receive "
        "a PerceptionAgent message."
    )


if __name__ == "__main__":
    main()