from pathlib import Path
import argparse
import json
import sys
import time


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from agents.perception_agent import PerceptionAgent
from agents.planner_agent import PlannerAgent


SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp"
}


class Orchestrator:
    """
    watchMe Orchestrator

    Coordinates input ingestion, perception, reasoning,
    action output, and trace logging.
    """

    def __init__(self):
        self.perception_agent = PerceptionAgent()
        self.planner_agent = PlannerAgent()


    def process_image(self, image_path):
        start_time = time.perf_counter()

        image_path = Path(image_path)

        perception_message = (
            self.perception_agent.perceive(
                image_path
            )
        )

        planner_message = (
            self.planner_agent.plan(
                perception_message
            )
        )

        total_processing_ms = round(
            (
                time.perf_counter()
                -
                start_time
            )
            *
            1000,
            2
        )

        result = {
            "input": {
                "image":
                    image_path.as_posix()
            },

            "perception":
                perception_message,

            "planning":
                planner_message,

            "final_action":
                planner_message.get(
                    "action",
                    {}
                ),

            "performance": {
                "total_processing_ms":
                    total_processing_ms
            }
        }

        trace_path = self.save_trace(
            image_path,
            result
        )

        result["trace_output"] = (
            trace_path
        )

        return result


    def save_trace(
        self,
        image_path,
        result
    ):
        trace_dir = (
            PROJECT_ROOT
            /
            "results"
            /
            "traces"
        )

        trace_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        trace_name = (
            f"{Path(image_path).stem}"
            f"_agent_trace.json"
        )

        trace_path = (
            trace_dir
            /
            trace_name
        )

        with open(
            trace_path,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                result,
                file,
                indent=4
            )

        return (
            trace_path
            .relative_to(
                PROJECT_ROOT
            )
            .as_posix()
        )


    def process_folder(
        self,
        folder_path
    ):
        folder_path = Path(
            folder_path
        )

        if not folder_path.exists():
            return {
                "status": "error",
                "reason":
                    "Input folder does not exist."
            }

        if not folder_path.is_dir():
            return {
                "status": "error",
                "reason":
                    "Input path is not a folder."
            }

        image_files = [
            path
            for path
            in sorted(
                folder_path.iterdir()
            )
            if (
                path.is_file()
                and
                path.suffix.lower()
                in
                SUPPORTED_EXTENSIONS
            )
        ]

        if not image_files:
            return {
                "status": "error",
                "reason":
                    "No supported image files "
                    "were found in the folder."
            }

        results = []

        for image_path in image_files:
            print(
                f"\nProcessing: "
                f"{image_path.name}"
            )

            result = (
                self.process_image(
                    image_path
                )
            )

            results.append(
                result
            )

            decision = (
                result
                .get(
                    "planning",
                    {}
                )
                .get(
                    "decision",
                    {}
                )
                .get(
                    "state"
                )
            )

            action = (
                result
                .get(
                    "final_action",
                    {}
                )
                .get(
                    "message"
                )
            )

            print(
                f"Decision: "
                f"{decision}"
            )

            print(
                f"Action: "
                f"{action}"
            )

        summary_path = (
            self.save_summary(
                folder_path,
                results
            )
        )

        return {
            "status":
                "success",

            "input_folder":
                folder_path.as_posix(),

            "images_processed":
                len(results),

            "summary_output":
                summary_path,

            "results":
                results
        }


    def save_summary(
        self,
        folder_path,
        results
    ):
        results_dir = (
            PROJECT_ROOT
            /
            "results"
        )

        results_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        decision_counts = {}

        compact_results = []

        for result in results:
            decision = (
                result
                .get(
                    "planning",
                    {}
                )
                .get(
                    "decision",
                    {}
                )
                .get(
                    "state",
                    "UNKNOWN"
                )
            )

            decision_counts[
                decision
            ] = (
                decision_counts.get(
                    decision,
                    0
                )
                +
                1
            )

            compact_results.append(
                {
                    "image":
                        result[
                            "input"
                        ][
                            "image"
                        ],

                    "decision":
                        decision,

                    "reason":
                        result
                        .get(
                            "planning",
                            {}
                        )
                        .get(
                            "decision",
                            {}
                        )
                        .get(
                            "reason"
                        ),

                    "action":
                        result
                        .get(
                            "final_action",
                            {}
                        )
                        .get(
                            "message"
                        ),

                    "trace":
                        result.get(
                            "trace_output"
                        )
                }
            )

        summary = {
            "status":
                "success",

            "input_folder":
                Path(
                    folder_path
                ).as_posix(),

            "images_processed":
                len(results),

            "decision_counts":
                decision_counts,

            "results":
                compact_results
        }

        summary_path = (
            results_dir
            /
            "batch_summary.json"
        )

        with open(
            summary_path,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                summary,
                file,
                indent=4
            )

        return (
            summary_path
            .relative_to(
                PROJECT_ROOT
            )
            .as_posix()
        )


def print_result(
    result
):
    print(
        json.dumps(
            result,
            indent=4
        )
    )


def main():
    parser = argparse.ArgumentParser(
        description=(
            "watchMe CV Agent Orchestrator"
        )
    )

    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help=(
            "Path to an image "
            "or folder of images."
        )
    )

    args = parser.parse_args()

    input_path = Path(
        args.input
    )

    orchestrator = (
        Orchestrator()
    )

    if input_path.is_file():
        result = (
            orchestrator.process_image(
                input_path
            )
        )

        print(
            "\nwatchMe Agent Result"
        )

        print(
            "--------------------"
        )

        print_result(
            result
        )

    elif input_path.is_dir():
        result = (
            orchestrator.process_folder(
                input_path
            )
        )

        print(
            "\nBatch Processing Complete"
        )

        print(
            "-------------------------"
        )

        print(
            f"Images processed: "
            f"{result.get('images_processed')}"
        )

        print(
            f"Summary: "
            f"{result.get('summary_output')}"
        )

    else:
        print(
            "Error: Input path "
            "does not exist."
        )


if __name__ == "__main__":
    main()