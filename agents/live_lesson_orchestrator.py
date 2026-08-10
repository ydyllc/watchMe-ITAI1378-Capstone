import cv2
import json
import threading
import time

from datetime import datetime
from pathlib import Path

from agents.perception_agent import PerceptionAgent
from agents.planner_agent import PlannerAgent
from agents.lesson_agent import LessonAgent


PROJECT_ROOT = Path(__file__).resolve().parent.parent

RESULTS_DIR = PROJECT_ROOT / "results"
TRACE_DIR = RESULTS_DIR / "traces"
LIVE_DIR = RESULTS_DIR / "live"

TRACE_DIR.mkdir(
    parents=True,
    exist_ok=True
)

LIVE_DIR.mkdir(
    parents=True,
    exist_ok=True
)


CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

ANALYZE_EVERY_N_FRAMES = 15

READY_CONFIRMATIONS_REQUIRED = 2

AUTO_START_COUNTDOWN_SECONDS = 3.0

MOUTH_MOVEMENT_THRESHOLD = 0.03


class LiveLessonOrchestrator:

    def __init__(
        self,
        lesson_type="cvc",
        input_mode="microphone"
    ):
        self.lesson_type = lesson_type
        self.input_mode = input_mode

        self.perception_agent = (
            PerceptionAgent()
        )

        self.planner_agent = (
            PlannerAgent()
        )

        self.lesson_agent = (
            LessonAgent()
        )

        # -------------------------------------------------
        # Session state
        # -------------------------------------------------

        self.session_state = (
            "WAITING_FOR_LEARNER"
        )

        self.current_decision = (
            "WAIT_FOR_USER"
        )

        self.current_reason = (
            "Waiting for learner."
        )

        self.current_action = (
            "Move into camera view."
        )

        self.last_error = None

        self.last_perception = None
        self.last_plan = None

        # -------------------------------------------------
        # Face perception
        # -------------------------------------------------

        self.face_detected = False
        self.face_count = 0
        self.face_centered = False
        self.face_position = "unknown"
        self.face_size_ratio = None
        self.face_box = None

        self.visual_readiness = (
            "no_face"
        )

        # -------------------------------------------------
        # Mouth perception
        # -------------------------------------------------

        self.mouth_analyzed = False
        self.mouth_visible = False

        self.previous_mouth_ratio = None

        self.mouth_movement_detected = (
            False
        )

        self.mouth_movement_events = 0

        self.max_mouth_delta = 0.0

        # -------------------------------------------------
        # Readiness / start state
        # -------------------------------------------------

        self.ready_confirmations = 0

        self.armed = False
        self.armed_time = None

        self.start_method = None

        # -------------------------------------------------
        # Lesson state
        # -------------------------------------------------

        self.lesson_running = False
        self.lesson_completed = False

        self.lesson_result = None
        self.lesson_error = None

        # Live lesson interface values

        self.lesson_phase = "waiting"

        self.lesson_prompt = None
        self.lesson_response = None
        self.lesson_outcome = None

        self.lesson_item_number = 0
        self.lesson_total_items = 0

        self.lesson_correct = 0
        self.lesson_near_match = 0
        self.lesson_incorrect = 0
        self.lesson_no_input = 0

        # -------------------------------------------------
        # Session tracking
        # -------------------------------------------------

        self.frame_count = 0
        self.perception_update_count = 0

        self.display_message = (
            "Move into camera view."
        )

        self.session_start = (
            datetime.now()
        )

        timestamp = (
            self.session_start.strftime(
                "%Y%m%d_%H%M%S"
            )
        )

        self.session_id = (
            f"live_lesson_{timestamp}"
        )

        self.snapshot_path = (
            LIVE_DIR
            /
            f"{self.session_id}_frame.jpg"
        )

        self.trace_path = (
            TRACE_DIR
            /
            f"{self.session_id}.json"
        )

    # -------------------------------------------------
    # Agent handoffs
    # -------------------------------------------------

    def run_perception(
        self,
        image_path
    ):
        return (
            self.perception_agent.perceive(
                image_path
            )
        )

    def run_planner(
        self,
        perception_message
    ):
        return (
            self.planner_agent.plan(
                perception_message
            )
        )

    # -------------------------------------------------
    # Read PerceptionAgent message
    # -------------------------------------------------

    def extract_perception(
        self,
        perception
    ):
        face = perception.get(
            "face",
            {}
        )

        mouth = perception.get(
            "mouth",
            {}
        )

        self.face_detected = bool(
            face.get(
                "detected",
                False
            )
        )

        self.face_count = int(
            face.get(
                "count",
                0
            )
            or
            0
        )

        self.face_centered = bool(
            face.get(
                "centered",
                False
            )
        )

        self.face_position = (
            face.get(
                "position",
                "unknown"
            )
        )

        self.face_size_ratio = (
            face.get(
                "size_ratio"
            )
        )

        self.visual_readiness = (
            perception.get(
                "visual_readiness",
                "no_face"
            )
        )

        self.mouth_analyzed = bool(
            mouth.get(
                "analyzed",
                False
            )
        )

        self.mouth_visible = bool(
            mouth.get(
                "visible",
                False
            )
        )

        boxes = face.get(
            "boxes",
            []
        )

        self.face_box = None

        if boxes:
            box = boxes[0]

            try:
                self.face_box = (
                    int(
                        box["x_min"]
                    ),
                    int(
                        box["y_min"]
                    ),
                    int(
                        box["x_max"]
                    ),
                    int(
                        box["y_max"]
                    )
                )

            except (
                KeyError,
                TypeError,
                ValueError
            ):
                self.face_box = None

        self.update_mouth_movement(
            mouth
        )

    # -------------------------------------------------
    # Read PlannerAgent message
    # -------------------------------------------------

    def extract_plan(
        self,
        plan
    ):
        decision = plan.get(
            "decision",
            {}
        )

        action = plan.get(
            "action",
            {}
        )

        self.current_decision = (
            decision.get(
                "state",
                "UNKNOWN"
            )
        )

        self.current_reason = (
            decision.get(
                "reason",
                ""
            )
        )

        self.current_action = (
            action.get(
                "message",
                ""
            )
        )

    # -------------------------------------------------
    # Mouth movement
    # -------------------------------------------------

    def update_mouth_movement(
        self,
        mouth
    ):
        mouth_ratio = mouth.get(
            "open_ratio"
        )

        if mouth_ratio is None:
            return

        try:
            mouth_ratio = float(
                mouth_ratio
            )

        except (
            TypeError,
            ValueError
        ):
            return

        if (
            self.previous_mouth_ratio
            is not None
        ):
            delta = abs(
                mouth_ratio
                -
                self.previous_mouth_ratio
            )

            if (
                delta
                >
                self.max_mouth_delta
            ):
                self.max_mouth_delta = (
                    delta
                )

            if (
                delta
                >=
                MOUTH_MOVEMENT_THRESHOLD
            ):
                self.mouth_movement_detected = (
                    True
                )

                self.mouth_movement_events += 1

        self.previous_mouth_ratio = (
            mouth_ratio
        )

    # -------------------------------------------------
    # Analyze one camera sample
    # -------------------------------------------------

    def analyze_frame(
        self,
        frame
    ):
        cv2.imwrite(
            str(
                self.snapshot_path
            ),
            frame
        )

        try:
            perception = (
                self.run_perception(
                    str(
                        self.snapshot_path
                    )
                )
            )

            self.last_perception = (
                perception
            )

            if (
                perception.get("status")
                !=
                "success"
            ):
                raise RuntimeError(
                    perception.get(
                        "reason",
                        "Perception failed."
                    )
                )

            self.perception_update_count += 1

            self.extract_perception(
                perception
            )

            plan = self.run_planner(
                perception
            )

            self.last_plan = plan

            self.extract_plan(
                plan
            )

            self.last_error = None

            self.update_session_state()

        except Exception as error:
            self.last_error = str(
                error
            )

            self.session_state = (
                "ERROR"
            )

            self.current_decision = (
                "ERROR"
            )

            self.cancel_armed_state()

            self.display_message = (
                "Integration error. "
                "Press M for demo override."
            )

            print()
            print(
                "Live integration error:"
            )

            print(
                self.last_error
            )

    # -------------------------------------------------
    # State machine
    # -------------------------------------------------

    def update_session_state(
        self
    ):
        if (
            self.lesson_running
            or
            self.lesson_completed
        ):
            return

        if (
            not self.face_detected
            or
            self.face_count == 0
        ):
            self.ready_confirmations = 0

            self.cancel_armed_state()

            self.session_state = (
                "WAITING_FOR_LEARNER"
            )

            self.display_message = (
                "Move into camera view."
            )

            return

        if self.face_count > 1:
            self.ready_confirmations = 0

            self.cancel_armed_state()

            self.session_state = (
                "POSITIONING"
            )

            self.display_message = (
                "Only one learner "
                "should be visible."
            )

            return

        if (
            self.current_decision
            ==
            "READY"
        ):
            self.ready_confirmations += 1

            if (
                self.ready_confirmations
                <
                READY_CONFIRMATIONS_REQUIRED
            ):
                self.session_state = (
                    "READY"
                )

                self.display_message = (
                    "Hold position..."
                )

                return

            if not self.armed:
                self.arm_lesson()

            return

        self.ready_confirmations = 0

        self.cancel_armed_state()

        self.session_state = (
            "POSITIONING"
        )

        self.display_message = (
            self.current_action
        )

    # -------------------------------------------------
    # Armed state
    # -------------------------------------------------

    def arm_lesson(
        self
    ):
        if (
            self.lesson_running
            or
            self.lesson_completed
        ):
            return

        self.armed = True

        self.armed_time = (
            time.monotonic()
        )

        self.session_state = (
            "ARMED"
        )

        self.display_message = (
            "Ready for lesson."
        )

        print()
        print(
            "Learner visually READY."
        )

        print(
            "Lesson ARMED."
        )

        print(
            "Automatic start in "
            f"{AUTO_START_COUNTDOWN_SECONDS:.0f} "
            "seconds."
        )

        print(
            "Press S to start sooner."
        )

    def cancel_armed_state(
        self
    ):
        if self.armed:
            print()
            print(
                "Readiness lost."
            )

            print(
                "Automatic start cancelled."
            )

        self.armed = False
        self.armed_time = None

    def get_countdown_remaining(
        self
    ):
        if (
            not self.armed
            or
            self.armed_time is None
        ):
            return None

        elapsed = (
            time.monotonic()
            -
            self.armed_time
        )

        return max(
            0.0,
            AUTO_START_COUNTDOWN_SECONDS
            -
            elapsed
        )

    def check_automatic_start(
        self
    ):
        if (
            not self.armed
            or
            self.lesson_running
            or
            self.lesson_completed
        ):
            return

        if (
            self.current_decision
            !=
            "READY"
        ):
            self.cancel_armed_state()
            return

        remaining = (
            self.get_countdown_remaining()
        )

        if (
            remaining is not None
            and
            remaining <= 0
        ):
            self.start_lesson(
                "automatic_countdown"
            )

    # -------------------------------------------------
    # Start methods
    # -------------------------------------------------

    def request_keyboard_start(
        self
    ):
        """
        S requires visual readiness.
        """

        if (
            self.lesson_running
            or
            self.lesson_completed
        ):
            return

        if (
            not self.armed
            or
            self.current_decision
            !=
            "READY"
        ):
            self.display_message = (
                "Cannot start. "
                "Learner must be READY."
            )

            print()
            print(
                "S ignored:"
            )

            print(
                "Learner must be READY."
            )

            return

        self.start_lesson(
            "keyboard_s"
        )

    def request_manual_override(
        self
    ):
        """
        M is the explicit demo fallback.

        This bypass is recorded in the trace.
        """

        if (
            self.lesson_running
            or
            self.lesson_completed
        ):
            return

        print()
        print(
            "MANUAL DEMO OVERRIDE"
        )

        print(
            "Visual readiness bypassed."
        )

        self.start_lesson(
            "manual_demo_override"
        )

    def start_lesson(
        self,
        start_method
    ):
        if (
            self.lesson_running
            or
            self.lesson_completed
        ):
            return

        self.start_method = (
            start_method
        )

        self.armed = False
        self.armed_time = None

        self.lesson_running = True

        self.session_state = (
            "LESSON_RUNNING"
        )

        self.lesson_phase = (
            "starting"
        )

        self.display_message = (
            "Lesson running. "
            "Follow the prompt."
        )

        print()
        print(
            "Starting lesson."
        )

        print(
            "Start method:",
            self.start_method
        )

        thread = threading.Thread(
            target=self.run_lesson,
            daemon=True
        )

        thread.start()

    # -------------------------------------------------
    # Live lesson callback
    # -------------------------------------------------

    def handle_lesson_status(
        self,
        status
    ):
        """
        Receive live status messages from
        LessonAgent and expose them to the
        camera interface.
        """

        event = status.get(
            "event"
        )

        if event == "lesson_started":

            self.lesson_phase = (
                "starting"
            )

            self.lesson_total_items = (
                status.get(
                    "total_items",
                    0
                )
            )

        elif event == "prompt":

            self.lesson_phase = (
                "prompt"
            )

            self.lesson_prompt = (
                status.get(
                    "prompt"
                )
            )

            self.lesson_response = None
            self.lesson_outcome = None

            self.lesson_item_number = (
                status.get(
                    "item_number",
                    0
                )
            )

            self.lesson_total_items = (
                status.get(
                    "total_items",
                    self.lesson_total_items
                )
            )

        elif event == "listening":

            self.lesson_phase = (
                "listening"
            )

            self.lesson_prompt = (
                status.get(
                    "prompt"
                )
            )

        elif event == (
            "waiting_for_typed_input"
        ):

            self.lesson_phase = (
                "waiting_for_input"
            )

            self.lesson_prompt = (
                status.get(
                    "prompt"
                )
            )

        elif event == "response":

            self.lesson_phase = (
                "response"
            )

            self.lesson_response = (
                status.get(
                    "response",
                    ""
                )
            )

        elif event == "outcome":

            self.lesson_phase = (
                "outcome"
            )

            self.lesson_prompt = (
                status.get(
                    "prompt"
                )
            )

            self.lesson_response = (
                status.get(
                    "response",
                    ""
                )
            )

            self.lesson_outcome = (
                status.get(
                    "outcome"
                )
            )

            if (
                self.lesson_outcome
                ==
                "CORRECT"
            ):
                self.lesson_correct += 1

            elif (
                self.lesson_outcome
                ==
                "NEAR_MATCH"
            ):
                self.lesson_near_match += 1

            elif (
                self.lesson_outcome
                ==
                "INCORRECT"
            ):
                self.lesson_incorrect += 1

            elif (
                self.lesson_outcome
                ==
                "NO_INPUT"
            ):
                self.lesson_no_input += 1

        elif event == "lesson_complete":

            self.lesson_phase = (
                "complete"
            )

    # -------------------------------------------------
    # Run LessonAgent
    # -------------------------------------------------

    def run_lesson(
        self
    ):
        try:
            self.lesson_result = (
                self.lesson_agent.run(
                    self.lesson_type,
                    input_mode=(
                        self.input_mode
                    ),
                    status_callback=(
                        self.handle_lesson_status
                    )
                )
            )

        except Exception as error:
            self.lesson_error = str(
                error
            )

            print()
            print(
                "Lesson error:"
            )

            print(
                self.lesson_error
            )

        finally:
            self.lesson_running = False
            self.lesson_completed = True

            self.lesson_phase = (
                "complete"
            )

            self.session_state = (
                "COMPLETE"
            )

            if self.lesson_error:
                self.display_message = (
                    "Lesson ended with error."
                )

            else:
                self.display_message = (
                    "Lesson complete."
                )

    # -------------------------------------------------
    # Bounding box
    # -------------------------------------------------

    def get_box_color(
        self
    ):
        """
        OpenCV BGR values:

        Blue:
        learner detected but not ready

        Green:
        learner ready
        """

        if (
            not self.face_detected
            or
            self.face_count <= 0
        ):
            return None

        if (
            self.current_decision
            ==
            "READY"
        ):
            return (
                0,
                255,
                0
            )

        return (
            255,
            0,
            0
        )

    def draw_face_box(
        self,
        frame
    ):
        if self.face_box is None:
            return

        color = self.get_box_color()

        if color is None:
            return

        (
            x1,
            y1,
            x2,
            y2
        ) = self.face_box

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            color,
            3
        )

        if (
            self.current_decision
            ==
            "READY"
        ):
            label = (
                "LEARNER READY"
            )

        else:
            label = (
                "LEARNER DETECTED"
            )

        cv2.putText(
            frame,
            label,
            (
                x1,
                max(
                    25,
                    y1 - 10
                )
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            color,
            2,
            cv2.LINE_AA
        )

    # -------------------------------------------------
    # Overlay text
    # -------------------------------------------------

    def draw_text(
        self,
        frame,
        text,
        y,
        scale=0.50,
        x=15
    ):
        text = str(
            text
        )

        cv2.putText(
            frame,
            text,
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            scale,
            (0, 0, 0),
            3,
            cv2.LINE_AA
        )

        cv2.putText(
            frame,
            text,
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            scale,
            (255, 255, 255),
            1,
            cv2.LINE_AA
        )

    # -------------------------------------------------
    # Live lesson learner interface
    # -------------------------------------------------

    def draw_lesson_interface(
        self,
        frame
    ):
        """
        Draw the current lesson prompt,
        listening state, response, and
        evaluation directly inside the
        webcam window.
        """

        if (
            not self.lesson_running
            and
            not self.lesson_completed
        ):
            return

        height = frame.shape[0]
        width = frame.shape[1]

        panel_top = 285
        panel_bottom = height - 82

        overlay = frame.copy()

        cv2.rectangle(
            overlay,
            (
                10,
                panel_top
            ),
            (
                width - 10,
                panel_bottom
            ),
            (
                0,
                0,
                0
            ),
            -1
        )

        cv2.addWeighted(
            overlay,
            0.68,
            frame,
            0.32,
            0,
            frame
        )

        lesson_title = (
            self.lesson_type
            .replace(
                "_",
                " "
            )
            .upper()
        )

        self.draw_text(
            frame,
            (
                f"{lesson_title} LESSON"
            ),
            panel_top + 25,
            scale=0.56
        )

        if self.lesson_total_items:

            self.draw_text(
                frame,
                (
                    f"Item "
                    f"{self.lesson_item_number}"
                    f"/"
                    f"{self.lesson_total_items}"
                ),
                panel_top + 50,
                scale=0.42
            )

        # -------------------------------------------------
        # Prompt
        # -------------------------------------------------

        if self.lesson_prompt:

            self.draw_text(
                frame,
                (
                    "SAY: "
                    f"{self.lesson_prompt.upper()}"
                ),
                panel_top + 82,
                scale=0.72
            )

        # -------------------------------------------------
        # Active listening
        # -------------------------------------------------

        if (
            self.lesson_phase
            ==
            "listening"
        ):

            self.draw_text(
                frame,
                "LISTENING...",
                panel_top + 112,
                scale=0.53
            )

        # -------------------------------------------------
        # Typed fallback
        # -------------------------------------------------

        elif (
            self.lesson_phase
            ==
            "waiting_for_input"
        ):

            self.draw_text(
                frame,
                "TYPE RESPONSE IN TERMINAL",
                panel_top + 112,
                scale=0.42
            )

        # -------------------------------------------------
        # Whisper response
        # -------------------------------------------------

        elif (
            self.lesson_phase
            ==
            "response"
        ):

            response_text = (
                self.lesson_response
                if self.lesson_response
                else
                "[no speech]"
            )

            self.draw_text(
                frame,
                (
                    "HEARD: "
                    f"{response_text[:35]}"
                ),
                panel_top + 112,
                scale=0.42
            )

        # -------------------------------------------------
        # Outcome
        # -------------------------------------------------

        elif (
            self.lesson_phase
            ==
            "outcome"
        ):

            response_text = (
                self.lesson_response
                if self.lesson_response
                else
                "[no speech]"
            )

            self.draw_text(
                frame,
                (
                    "HEARD: "
                    f"{response_text[:30]}"
                ),
                panel_top + 105,
                scale=0.40
            )

            self.draw_text(
                frame,
                (
                    "RESULT: "
                    f"{self.lesson_outcome}"
                ),
                panel_top + 132,
                scale=0.51
            )

        # -------------------------------------------------
        # Complete
        # -------------------------------------------------

        elif (
            self.lesson_phase
            ==
            "complete"
        ):

            self.draw_text(
                frame,
                "LESSON COMPLETE",
                panel_top + 82,
                scale=0.58
            )

            self.draw_text(
                frame,
                (
                    "Correct: "
                    f"{self.lesson_correct}   "
                    "Near: "
                    f"{self.lesson_near_match}   "
                    "Incorrect: "
                    f"{self.lesson_incorrect}"
                ),
                panel_top + 112,
                scale=0.40
            )

            self.draw_text(
                frame,
                (
                    "No input: "
                    f"{self.lesson_no_input}"
                ),
                panel_top + 137,
                scale=0.40
            )

    # -------------------------------------------------
    # Main overlay
    # -------------------------------------------------

    def draw_overlay(
        self,
        frame
    ):
        self.draw_face_box(
            frame
        )

        self.draw_text(
            frame,
            "watchMe Live Lesson",
            25,
            scale=0.65
        )

        self.draw_text(
            frame,
            (
                "State: "
                f"{self.session_state}"
            ),
            55
        )

        self.draw_text(
            frame,
            (
                "Decision: "
                f"{self.current_decision}"
            ),
            82
        )

        self.draw_text(
            frame,
            (
                "Visual readiness: "
                f"{self.visual_readiness}"
            ),
            109
        )

        self.draw_text(
            frame,
            (
                "Faces: "
                f"{self.face_count}"
            ),
            136
        )

        self.draw_text(
            frame,
            (
                "Position: "
                f"{self.face_position}"
            ),
            163
        )

        if (
            self.face_size_ratio
            is not None
        ):
            self.draw_text(
                frame,
                (
                    "Face size: "
                    f"{float(self.face_size_ratio):.3f}"
                ),
                190
            )

        self.draw_text(
            frame,
            (
                "Lesson: "
                f"{self.lesson_type}"
            ),
            217
        )

        movement_text = (
            "YES"
            if
            self.mouth_movement_detected
            else
            "NO"
        )

        self.draw_text(
            frame,
            (
                "Mouth movement: "
                f"{movement_text}"
            ),
            244
        )

        # -------------------------------------------------
        # Pre-lesson states
        # -------------------------------------------------

        if self.armed:

            remaining = (
                self.get_countdown_remaining()
            )

            if remaining is not None:

                countdown_number = max(
                    1,
                    int(
                        remaining
                        +
                        0.999
                    )
                )

                self.draw_text(
                    frame,
                    (
                        "READY - starting in "
                        f"{countdown_number}"
                    ),
                    277,
                    scale=0.58
                )

        elif (
            not self.lesson_running
            and
            not self.lesson_completed
        ):

            self.draw_text(
                frame,
                self.display_message,
                277
            )

        # -------------------------------------------------
        # Active lesson panel
        # -------------------------------------------------

        self.draw_lesson_interface(
            frame
        )

        # -------------------------------------------------
        # Controls
        # -------------------------------------------------

        if (
            not self.lesson_running
            and
            not self.lesson_completed
        ):

            self.draw_text(
                frame,
                "S = start early when READY",
                frame.shape[0] - 72,
                scale=0.40
            )

            self.draw_text(
                frame,
                "M = manual demo override",
                frame.shape[0] - 46,
                scale=0.40
            )

        self.draw_text(
            frame,
            "Q = save trace and quit",
            frame.shape[0] - 20,
            scale=0.40
        )

        if self.last_error:

            self.draw_text(
                frame,
                (
                    "ERROR: "
                    f"{self.last_error[:55]}"
                ),
                270,
                scale=0.36
            )

    # -------------------------------------------------
    # Session trace
    # -------------------------------------------------

    def save_trace(
        self
    ):
        end_time = (
            datetime.now()
        )

        duration_seconds = (
            end_time
            -
            self.session_start
        ).total_seconds()

        trace = {
            "session_id": (
                self.session_id
            ),

            "agent": (
                "LiveLessonOrchestrator"
            ),

            "session_state": (
                self.session_state
            ),

            "lesson_type": (
                self.lesson_type
            ),

            "input_mode": (
                self.input_mode
            ),

            "start_method": (
                self.start_method
            ),

            "camera": {
                "camera_index": (
                    CAMERA_INDEX
                ),

                "frames_processed": (
                    self.frame_count
                ),

                "perception_updates": (
                    self.perception_update_count
                ),

                "face_detected": (
                    self.face_detected
                ),

                "face_count": (
                    self.face_count
                ),

                "face_centered": (
                    self.face_centered
                ),

                "face_position": (
                    self.face_position
                ),

                "face_size_ratio": (
                    self.face_size_ratio
                ),

                "visual_readiness": (
                    self.visual_readiness
                ),

                "face_box": (
                    self.face_box
                )
            },

            "planner": {
                "final_decision": (
                    self.current_decision
                ),

                "final_reason": (
                    self.current_reason
                ),

                "final_action": (
                    self.current_action
                ),

                "integration_error": (
                    self.last_error
                )
            },

            "mouth_movement": {
                "detected": (
                    self.mouth_movement_detected
                ),

                "movement_events": (
                    self.mouth_movement_events
                ),

                "max_delta": (
                    self.max_mouth_delta
                ),

                "threshold": (
                    MOUTH_MOVEMENT_THRESHOLD
                )
            },

            "lesson_interface": {
                "phase": (
                    self.lesson_phase
                ),

                "current_prompt": (
                    self.lesson_prompt
                ),

                "last_response": (
                    self.lesson_response
                ),

                "last_outcome": (
                    self.lesson_outcome
                ),

                "item_number": (
                    self.lesson_item_number
                ),

                "total_items": (
                    self.lesson_total_items
                ),

                "correct": (
                    self.lesson_correct
                ),

                "near_match": (
                    self.lesson_near_match
                ),

                "incorrect": (
                    self.lesson_incorrect
                ),

                "no_input": (
                    self.lesson_no_input
                )
            },

            "lesson": {
                "completed": (
                    self.lesson_completed
                ),

                "error": (
                    self.lesson_error
                ),

                "result": (
                    self.lesson_result
                )
            },

            "timing": {
                "started": (
                    self.session_start
                    .isoformat()
                ),

                "ended": (
                    end_time.isoformat()
                ),

                "duration_seconds": (
                    duration_seconds
                )
            }
        }

        with open(
            self.trace_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                trace,
                file,
                indent=2
            )

        return trace

    # -------------------------------------------------
    # Main live loop
    # -------------------------------------------------

    def run(
        self
    ):
        camera = cv2.VideoCapture(
            CAMERA_INDEX
        )

        camera.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            FRAME_WIDTH
        )

        camera.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            FRAME_HEIGHT
        )

        if not camera.isOpened():

            print(
                "ERROR: Could not open "
                f"camera {CAMERA_INDEX}."
            )

            return

        print()
        print(
            "watchMe Live Lesson"
        )

        print(
            "-------------------"
        )

        print(
            "Lesson:",
            self.lesson_type
        )

        print(
            "Input mode:",
            self.input_mode
        )

        print()
        print(
            "Blue box = learner detected "
            "but not ready."
        )

        print(
            "Green box = learner ready."
        )

        print()
        print(
            "Automatic:"
        )

        print(
            "READY -> ARMED -> "
            "3 second countdown -> lesson"
        )

        print()
        print(
            "During the lesson, the webcam "
            "window displays the prompt, "
            "listening state, response, "
            "and outcome."
        )

        print()
        print(
            "S = start early when READY"
        )

        print(
            "M = manual demo override"
        )

        print(
            "Q = save trace and quit"
        )

        while True:

            success, frame = (
                camera.read()
            )

            if not success:

                print(
                    "Camera frame could "
                    "not be read."
                )

                break

            self.frame_count += 1

            if (
                self.frame_count
                %
                ANALYZE_EVERY_N_FRAMES
                ==
                0
            ):

                self.analyze_frame(
                    frame
                )

            self.check_automatic_start()

            display_frame = (
                frame.copy()
            )

            self.draw_overlay(
                display_frame
            )

            cv2.imshow(
                "watchMe Live Lesson",
                display_frame
            )

            key = (
                cv2.waitKey(1)
                &
                0xFF
            )

            if key in [
                ord("s"),
                ord("S")
            ]:

                self.request_keyboard_start()

            elif key in [
                ord("m"),
                ord("M")
            ]:

                self.request_manual_override()

            elif key in [
                ord("q"),
                ord("Q")
            ]:

                break

        camera.release()

        cv2.destroyAllWindows()

        trace = (
            self.save_trace()
        )

        print()
        print(
            "Live Lesson Result"
        )

        print(
            "------------------"
        )

        print(
            "Session:",
            self.session_id
        )

        print(
            "Frames:",
            self.frame_count
        )

        print(
            "Perception updates:",
            self.perception_update_count
        )

        print(
            "Face detected:",
            self.face_detected
        )

        print(
            "Face count:",
            self.face_count
        )

        print(
            "Final visual readiness:",
            self.visual_readiness
        )

        print(
            "Final state:",
            self.session_state
        )

        print(
            "Start method:",
            self.start_method
        )

        print(
            "Mouth movement:",
            self.mouth_movement_detected
        )

        print(
            "Movement events:",
            self.mouth_movement_events
        )

        print(
            "Max mouth delta:",
            round(
                self.max_mouth_delta,
                4
            )
        )

        print(
            "Lesson completed:",
            self.lesson_completed
        )

        if self.lesson_completed:

            print(
                "Lesson score:",
                (
                    f"{self.lesson_correct} correct, "
                    f"{self.lesson_near_match} near match, "
                    f"{self.lesson_incorrect} incorrect, "
                    f"{self.lesson_no_input} no input"
                )
            )

        if self.last_error:

            print()
            print(
                "Integration error:"
            )

            print(
                self.last_error
            )

        if self.lesson_result:

            print()
            print(
                "Lesson result:"
            )

            print(
                self.lesson_result
            )

        if self.lesson_error:

            print()
            print(
                "Lesson error:"
            )

            print(
                self.lesson_error
            )

        print()
        print(
            "Trace:",
            self.trace_path
        )

        return trace


def choose_lesson():

    print()
    print(
        "Choose a lesson:"
    )

    print(
        "1. CVC"
    )

    print(
        "2. Shapes"
    )

    choice = input(
        "Selection: "
    ).strip()

    if choice == "2":
        return "shapes"

    return "cvc"


def choose_input_mode():

    print()
    print(
        "Choose input mode:"
    )

    print(
        "1. Typed"
    )

    print(
        "2. Microphone + Whisper"
    )

    choice = input(
        "Selection: "
    ).strip()

    if choice == "1":
        return "typed"

    return "microphone"


def main():

    lesson_type = (
        choose_lesson()
    )

    input_mode = (
        choose_input_mode()
    )

    orchestrator = (
        LiveLessonOrchestrator(
            lesson_type=lesson_type,
            input_mode=input_mode
        )
    )

    orchestrator.run()


if __name__ == "__main__":
    main()