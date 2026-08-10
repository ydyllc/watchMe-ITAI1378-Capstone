from pathlib import Path
import json
import sys
import time


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from agents.orchestrator import Orchestrator


EVALUATION_FILE = PROJECT_ROOT / "data" / "evaluation_cases.json"
RESULTS_DIR = PROJECT_ROOT / "results"


def load_cases():
    if not EVALUATION_FILE.exists():
        raise FileNotFoundError(
            f"Evaluation file not found: {EVALUATION_FILE}"
        )

    with open(
        EVALUATION_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def get_actual_decision(result):
    planning = result.get(
        "planning",
        {}
    )

    decision = planning.get(
        "decision",
        {}
    )

    return decision.get(
        "state",
        "UNKNOWN"
    )


def evaluate_case(
    orchestrator,
    case
):
    start_time = time.perf_counter()

    image_path = case["image"]

    result = orchestrator.process_image(
        image_path
    )

    actual_decision = get_actual_decision(
        result
    )

    expected_decision = case[
        "expected_decision"
    ]

    passed = (
        actual_decision
        ==
        expected_decision
    )

    latency_ms = round(
        (
            time.perf_counter()
            -
            start_time
        )
        *
        1000,
        2
    )

    return {
        "id": case["id"],
        "image": image_path,
        "category": case.get(
            "category"
        ),
        "expected_decision":
            expected_decision,
        "actual_decision":
            actual_decision,
        "passed":
            passed,
        "latency_ms":
            latency_ms,
        "trace_output":
            result.get(
                "trace_output"
            )
    }


def save_json_results(
    evaluation_results
):
    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = (
        RESULTS_DIR
        /
        "evaluation_results.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            evaluation_results,
            file,
            indent=4
        )

    return output_path


def save_metrics(
    total_cases,
    passed_cases,
    failed_cases,
    success_rate,
    average_latency
):
    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    metrics_path = (
        RESULTS_DIR
        /
        "metrics.txt"
    )

    text = (
        "watchMe Agent Evaluation Metrics\n"
        "================================\n\n"
        f"Total scenarios: {total_cases}\n"
        f"Passed scenarios: {passed_cases}\n"
        f"Failed scenarios: {failed_cases}\n"
        f"Task success rate: {success_rate:.2f}%\n"
        f"Average end-to-end latency: "
        f"{average_latency:.2f} ms\n"
    )

    with open(
        metrics_path,
        "w",
        encoding="utf-8"
    ) as file:
        file.write(text)

    return metrics_path


def main():
    print(
        "\nwatchMe Agent Evaluation"
    )

    print(
        "------------------------"
    )

    cases = load_cases()

    orchestrator = Orchestrator()

    results = []

    for case in cases:
        print(
            f"\nRunning {case['id']}: "
            f"{case['image']}"
        )

        evaluation = evaluate_case(
            orchestrator,
            case
        )

        results.append(
            evaluation
        )

        print(
            f"Expected: "
            f"{evaluation['expected_decision']}"
        )

        print(
            f"Actual: "
            f"{evaluation['actual_decision']}"
        )

        print(
            "Result: "
            +
            (
                "PASS"
                if evaluation["passed"]
                else "FAIL"
            )
        )

    total_cases = len(
        results
    )

    passed_cases = sum(
        1
        for result in results
        if result["passed"]
    )

    failed_cases = (
        total_cases
        -
        passed_cases
    )

    if total_cases > 0:
        success_rate = (
            passed_cases
            /
            total_cases
        ) * 100
    else:
        success_rate = 0.0

    latencies = [
        result["latency_ms"]
        for result in results
    ]

    average_latency = (
        sum(latencies)
        /
        len(latencies)
        if latencies
        else 0.0
    )

    evaluation_summary = {
        "total_cases":
            total_cases,

        "passed_cases":
            passed_cases,

        "failed_cases":
            failed_cases,

        "task_success_rate_percent":
            round(
                success_rate,
                2
            ),

        "average_latency_ms":
            round(
                average_latency,
                2
            ),

        "results":
            results
    }

    json_path = save_json_results(
        evaluation_summary
    )

    metrics_path = save_metrics(
        total_cases,
        passed_cases,
        failed_cases,
        success_rate,
        average_latency
    )

    print(
        "\nEvaluation Complete"
    )

    print(
        "-------------------"
    )

    print(
        f"Scenarios: "
        f"{total_cases}"
    )

    print(
        f"Passed: "
        f"{passed_cases}"
    )

    print(
        f"Failed: "
        f"{failed_cases}"
    )

    print(
        f"Success rate: "
        f"{success_rate:.2f}%"
    )

    print(
        f"Average latency: "
        f"{average_latency:.2f} ms"
    )

    print(
        f"JSON results: "
        f"{json_path.relative_to(PROJECT_ROOT).as_posix()}"
    )

    print(
        f"Metrics: "
        f"{metrics_path.relative_to(PROJECT_ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()