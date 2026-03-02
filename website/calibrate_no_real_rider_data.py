"""Grid-search MOTOMAP ETA parameters without real rider telemetry.

This CLI calibrates `MOTOMAP_SPEED_FACTOR` and `MOTOMAP_SEGMENT_DELAY_S`
by repeatedly running `evaluate_with_google.py` on the same evaluation setup.
Each candidate is scored using:

- aggregate failed-check ratio (primary)
- average standard-route time ratio mismatch vs baseline
- average standard-route distance ratio mismatch vs baseline

The final JSON report contains all candidate runs plus the best candidate.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import time
from contextlib import nullcontext
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

DEFAULT_SPEED_FACTORS = "0.45,0.55,0.65,0.75"
DEFAULT_SEGMENT_DELAYS = "0.0,1.0,2.0,3.0"
DEFAULT_OUTPUT_JSON = Path("routes") / "no_real_rider_data_calibration_report.json"
DEFAULT_EVAL_SCRIPT = "evaluate_with_google.py"
DEFAULT_PLACE = "Kadikoy, Istanbul, Turkey"
DEFAULT_VALHALLA_URL = "https://valhalla1.openstreetmap.de"
MIN_SPEED_FACTOR = 0.2
MAX_SPEED_FACTOR = 1.0
MIN_SEGMENT_DELAY_S = 0.0
MAX_SEGMENT_DELAY_S = 8.0


@dataclass(frozen=True)
class Candidate:
    index: int
    speed_factor: float
    segment_delay_s: float

    @property
    def label(self) -> str:
        return f"speed_factor={self.speed_factor:.4g}, segment_delay_s={self.segment_delay_s:.4g}"


@dataclass(frozen=True)
class ObjectiveWeights:
    failure_weight: float
    time_mismatch_weight: float
    distance_mismatch_weight: float
    missing_ratio_penalty: float
    failed_run_penalty: float


class RichHelpFormatter(
    argparse.ArgumentDefaultsHelpFormatter,
    argparse.RawTextHelpFormatter,
):
    """Keep default values and preserve line breaks in epilog examples."""


def parse_csv_floats(raw: str, arg_name: str) -> list[float]:
    values: list[float] = []
    seen: set[float] = set()
    normalized = raw.replace(";", ",")
    for token in normalized.split(","):
        token = token.strip()
        if not token:
            continue
        try:
            value = float(token)
        except ValueError as exc:
            raise ValueError(f"Invalid float in --{arg_name}: '{token}'") from exc
        key = round(value, 10)
        if key in seen:
            continue
        seen.add(key)
        values.append(value)

    if not values:
        raise ValueError(f"--{arg_name} must contain at least one float value.")

    return values


def validate_candidates(speed_factors: list[float], segment_delays: list[float]) -> None:
    for value in speed_factors:
        if not (MIN_SPEED_FACTOR <= value <= MAX_SPEED_FACTOR):
            raise ValueError(
                f"Speed factor {value} is out of range "
                f"[{MIN_SPEED_FACTOR}, {MAX_SPEED_FACTOR}]."
            )
    for value in segment_delays:
        if not (MIN_SEGMENT_DELAY_S <= value <= MAX_SEGMENT_DELAY_S):
            raise ValueError(
                f"Segment delay {value} is out of range "
                f"[{MIN_SEGMENT_DELAY_S}, {MAX_SEGMENT_DELAY_S}]."
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Calibrate MOTOMAP speed/delay parameters with no real rider data by "
            "grid-searching candidate values against evaluate_with_google.py outputs."
        ),
        formatter_class=RichHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python calibrate_no_real_rider_data.py --batch 20 --backend google\n"
            "  python calibrate_no_real_rider_data.py --pairs-file routes/od_pairs.json "
            "--speed-factors 0.5,0.6,0.7 --segment-delays 1,2,3\n"
            "  python calibrate_no_real_rider_data.py --backend valhalla "
            "--valhalla-url https://valhalla1.openstreetmap.de"
        ),
    )
    parser.add_argument(
        "--speed-factors",
        default=DEFAULT_SPEED_FACTORS,
        help="Comma-separated candidate values for MOTOMAP_SPEED_FACTOR.",
    )
    parser.add_argument(
        "--segment-delays",
        default=DEFAULT_SEGMENT_DELAYS,
        help="Comma-separated candidate values for MOTOMAP_SEGMENT_DELAY_S.",
    )
    parser.add_argument(
        "--evaluation-script",
        default=DEFAULT_EVAL_SCRIPT,
        help="Path to evaluation CLI to execute for each candidate.",
    )
    parser.add_argument(
        "--output-json",
        default=str(DEFAULT_OUTPUT_JSON),
        help="Final calibration report path.",
    )
    parser.add_argument(
        "--artifacts-dir",
        help=(
            "Optional directory to persist per-candidate evaluation JSON files. "
            "If omitted, temporary files are cleaned up automatically."
        ),
    )

    # Evaluation forwarding options.
    parser.add_argument(
        "--batch",
        type=int,
        default=20,
        help="Number of O-D samples to evaluate per candidate.",
    )
    parser.add_argument(
        "--pairs-file",
        help="Optional explicit O-D pairs JSON file passed to evaluation script.",
    )
    parser.add_argument(
        "--place",
        default=DEFAULT_PLACE,
        help="Place string passed to evaluation script.",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed for O-D sampling.")
    parser.add_argument(
        "--min-distance-m",
        type=float,
        default=1000.0,
        help="Minimum crow-fly O-D distance for sampled pairs.",
    )
    parser.add_argument(
        "--max-distance-m",
        type=float,
        default=10000.0,
        help="Maximum crow-fly O-D distance for sampled pairs.",
    )
    parser.add_argument(
        "--backend",
        choices=["google", "valhalla"],
        default="google",
        help="Baseline backend passed to evaluation script.",
    )
    parser.add_argument(
        "--valhalla-url",
        default=DEFAULT_VALHALLA_URL,
        help="Valhalla base URL used when --backend=valhalla.",
    )
    parser.add_argument(
        "--timeout-s",
        type=float,
        default=1800.0,
        help="Per-candidate subprocess timeout in seconds.",
    )

    # Objective scoring controls.
    parser.add_argument(
        "--failure-weight",
        type=float,
        default=100.0,
        help="Weight for failed-check ratio in objective score.",
    )
    parser.add_argument(
        "--time-mismatch-weight",
        type=float,
        default=12.0,
        help="Weight for average abs(1 - std_time_ratio_vs_baseline).",
    )
    parser.add_argument(
        "--distance-mismatch-weight",
        type=float,
        default=10.0,
        help="Weight for average abs(1 - std_distance_ratio_vs_baseline).",
    )
    parser.add_argument(
        "--missing-ratio-penalty",
        type=float,
        default=1.0,
        help="Mismatch value used when no valid ratio metrics are available.",
    )
    parser.add_argument(
        "--failed-run-penalty",
        type=float,
        default=1000.0,
        help="Objective score assigned when subprocess run itself fails.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned candidate grid and stop without executing evaluations.",
    )

    return parser.parse_args()


def resolve_path(path: str, script_dir: Path) -> Path:
    raw = Path(path)
    if raw.is_absolute():
        return raw
    return script_dir / raw


def to_safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(result):
        return None
    return result


def mean_or_none(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def truncate_tail(text: str, max_chars: int = 2000) -> str:
    if len(text) <= max_chars:
        return text
    return text[-max_chars:]


def get_case_ratio(case: dict[str, Any], key_baseline: str, key_legacy: str) -> float | None:
    metrics = case.get("metrics")
    if not isinstance(metrics, dict):
        return None
    value = to_safe_float(metrics.get(key_baseline))
    if value is None:
        value = to_safe_float(metrics.get(key_legacy))
    return value


def extract_aggregate_metrics(summary: dict[str, Any]) -> dict[str, Any]:
    batch = summary.get("batch")
    if not isinstance(batch, dict):
        raise ValueError("Evaluation summary JSON is missing a 'batch' section.")

    cases_raw = batch.get("cases")
    cases: list[dict[str, Any]] = [
        case for case in (cases_raw or []) if isinstance(case, dict)
    ]
    failed_checks = batch.get("failed_checks")
    if not isinstance(failed_checks, dict):
        failed_checks = {}

    count_evaluated = int(to_safe_float(batch.get("count_evaluated")) or len(cases))
    full_pass = int(to_safe_float(batch.get("full_pass")) or 0)

    checks_per_case = 0
    for case in cases:
        checks = case.get("checks")
        if isinstance(checks, dict) and checks:
            checks_per_case = max(checks_per_case, len(checks))
    if checks_per_case == 0:
        checks_per_case = len(failed_checks)

    total_failed_checks = 0
    for value in failed_checks.values():
        total_failed_checks += int(to_safe_float(value) or 0)

    total_checks = None
    if count_evaluated > 0 and checks_per_case > 0:
        total_checks = count_evaluated * checks_per_case

    failure_ratio = None
    if total_checks:
        failure_ratio = total_failed_checks / total_checks

    time_mismatch_values: list[float] = []
    distance_mismatch_values: list[float] = []
    for case in cases:
        time_ratio = get_case_ratio(
            case,
            key_baseline="std_time_ratio_vs_baseline",
            key_legacy="std_time_ratio_vs_google",
        )
        if time_ratio is not None:
            time_mismatch_values.append(abs(1.0 - time_ratio))

        distance_ratio = get_case_ratio(
            case,
            key_baseline="std_distance_ratio_vs_baseline",
            key_legacy="std_distance_ratio_vs_google",
        )
        if distance_ratio is not None:
            distance_mismatch_values.append(abs(1.0 - distance_ratio))

    error_case_count = sum(1 for case in cases if str(case.get("status")) == "ERROR")

    return {
        "count_evaluated": count_evaluated,
        "full_pass": full_pass,
        "full_pass_rate": (full_pass / count_evaluated) if count_evaluated > 0 else None,
        "checks_per_case": checks_per_case,
        "total_checks": total_checks,
        "failed_checks": failed_checks,
        "total_failed_checks": total_failed_checks,
        "failure_ratio": failure_ratio,
        "error_case_count": error_case_count,
        "time_ratio_count": len(time_mismatch_values),
        "distance_ratio_count": len(distance_mismatch_values),
        "avg_time_mismatch": mean_or_none(time_mismatch_values),
        "avg_distance_mismatch": mean_or_none(distance_mismatch_values),
    }


def compute_objective(
    status: str,
    aggregate: dict[str, Any] | None,
    weights: ObjectiveWeights,
) -> tuple[float, dict[str, Any]]:
    if status != "ok" or aggregate is None:
        failed_run_penalty = float(weights.failed_run_penalty)
        return failed_run_penalty, {
            "failure_component": None,
            "time_mismatch_component": None,
            "distance_mismatch_component": None,
            "failed_run_penalty": failed_run_penalty,
        }

    failure_ratio = to_safe_float(aggregate.get("failure_ratio"))
    if failure_ratio is None:
        failure_ratio = 1.0

    avg_time_mismatch = to_safe_float(aggregate.get("avg_time_mismatch"))
    if avg_time_mismatch is None:
        avg_time_mismatch = weights.missing_ratio_penalty

    avg_distance_mismatch = to_safe_float(aggregate.get("avg_distance_mismatch"))
    if avg_distance_mismatch is None:
        avg_distance_mismatch = weights.missing_ratio_penalty

    failure_component = weights.failure_weight * failure_ratio
    time_component = weights.time_mismatch_weight * avg_time_mismatch
    distance_component = weights.distance_mismatch_weight * avg_distance_mismatch

    total = failure_component + time_component + distance_component
    return total, {
        "failure_component": failure_component,
        "time_mismatch_component": time_component,
        "distance_mismatch_component": distance_component,
        "failed_run_penalty": 0.0,
    }


def build_candidates(speed_factors: list[float], segment_delays: list[float]) -> list[Candidate]:
    candidates: list[Candidate] = []
    index = 1
    for speed_factor in speed_factors:
        for segment_delay_s in segment_delays:
            candidates.append(
                Candidate(
                    index=index,
                    speed_factor=speed_factor,
                    segment_delay_s=segment_delay_s,
                )
            )
            index += 1
    return candidates


def candidate_slug(candidate: Candidate) -> str:
    speed = f"{candidate.speed_factor:.5f}".replace("-", "m").replace(".", "p")
    delay = f"{candidate.segment_delay_s:.5f}".replace("-", "m").replace(".", "p")
    return f"c{candidate.index:03d}_sf_{speed}_sd_{delay}"


def run_candidate(
    *,
    candidate: Candidate,
    eval_script: Path,
    script_dir: Path,
    args: argparse.Namespace,
    run_dir: Path,
    keep_artifacts: bool,
    weights: ObjectiveWeights,
) -> dict[str, Any]:
    run_started = time.perf_counter()
    slug = candidate_slug(candidate)
    eval_output_json = run_dir / f"{slug}.json"

    command = [
        sys.executable,
        str(eval_script),
        "--skip-single",
        "--batch",
        str(max(0, args.batch)),
        "--place",
        args.place,
        "--seed",
        str(args.seed),
        "--min-distance-m",
        str(args.min_distance_m),
        "--max-distance-m",
        str(args.max_distance_m),
        "--backend",
        args.backend,
        "--valhalla-url",
        args.valhalla_url,
        "--output-json",
        str(eval_output_json),
    ]

    if args.pairs_file:
        command.extend(["--pairs-file", str(args.pairs_file)])

    env = os.environ.copy()
    env["MOTOMAP_SPEED_FACTOR"] = f"{candidate.speed_factor:.8g}"
    env["MOTOMAP_SEGMENT_DELAY_S"] = f"{candidate.segment_delay_s:.8g}"
    env.setdefault("PYTHONUTF8", "1")

    status = "ok"
    return_code: int | None = None
    stdout_text = ""
    stderr_text = ""
    aggregate: dict[str, Any] | None = None
    error_message: str | None = None

    try:
        completed = subprocess.run(
            command,
            cwd=str(script_dir),
            env=env,
            capture_output=True,
            text=True,
            check=False,
            timeout=max(1.0, float(args.timeout_s)),
        )
        return_code = completed.returncode
        stdout_text = completed.stdout or ""
        stderr_text = completed.stderr or ""
        if completed.returncode != 0:
            status = "subprocess_failed"
            error_message = f"Evaluation subprocess exited with code {completed.returncode}."
    except subprocess.TimeoutExpired as exc:
        status = "timeout"
        error_message = f"Timed out after {args.timeout_s} seconds."
        stdout_text = (exc.stdout or "") if isinstance(exc.stdout, str) else ""
        stderr_text = (exc.stderr or "") if isinstance(exc.stderr, str) else ""
    except OSError as exc:
        status = "subprocess_error"
        error_message = f"Subprocess execution failed: {exc}"

    if status == "ok":
        if not eval_output_json.exists():
            status = "missing_output_json"
            error_message = "Evaluation completed but output JSON file was not created."
        else:
            try:
                summary = json.loads(eval_output_json.read_text(encoding="utf-8"))
                aggregate = extract_aggregate_metrics(summary)
            except (OSError, json.JSONDecodeError, ValueError) as exc:
                status = "invalid_output_json"
                error_message = f"Failed to read/parse evaluation JSON: {exc}"

    objective_score, objective_breakdown = compute_objective(
        status=status,
        aggregate=aggregate,
        weights=weights,
    )
    run_duration_s = round(time.perf_counter() - run_started, 3)

    return {
        "candidate_index": candidate.index,
        "speed_factor": candidate.speed_factor,
        "segment_delay_s": candidate.segment_delay_s,
        "status": status,
        "objective_score": objective_score,
        "objective_breakdown": objective_breakdown,
        "duration_s": run_duration_s,
        "subprocess_return_code": return_code,
        "command": command,
        "aggregate": aggregate,
        "error": error_message,
        "stdout_tail": truncate_tail(stdout_text),
        "stderr_tail": truncate_tail(stderr_text),
        "evaluation_json_path": str(eval_output_json) if keep_artifacts else None,
    }


def select_best_result(results: list[dict[str, Any]]) -> dict[str, Any] | None:
    valid = [
        result
        for result in results
        if isinstance(to_safe_float(result.get("objective_score")), float)
    ]
    if not valid:
        return None

    ok_results = [result for result in valid if result.get("status") == "ok"]
    pool = ok_results if ok_results else valid

    def key_fn(item: dict[str, Any]) -> tuple[float, float, float]:
        return (
            float(item.get("objective_score", float("inf"))),
            float(item.get("speed_factor", float("inf"))),
            float(item.get("segment_delay_s", float("inf"))),
        )

    return min(pool, key=key_fn)


def main() -> None:
    args = parse_args()
    script_dir = Path(__file__).resolve().parent

    try:
        speed_factors = parse_csv_floats(args.speed_factors, "speed-factors")
        segment_delays = parse_csv_floats(args.segment_delays, "segment-delays")
        validate_candidates(speed_factors, segment_delays)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    if args.batch <= 0 and not args.pairs_file:
        raise SystemExit("Provide --batch > 0 or --pairs-file so each candidate has evaluation data.")
    if args.min_distance_m <= 0:
        raise SystemExit("--min-distance-m must be > 0.")
    if args.max_distance_m <= args.min_distance_m:
        raise SystemExit("--max-distance-m must be greater than --min-distance-m.")

    eval_script = resolve_path(args.evaluation_script, script_dir)
    if not eval_script.exists():
        raise SystemExit(f"Evaluation script not found: {eval_script}")

    pairs_file = None
    if args.pairs_file:
        pairs_file = resolve_path(args.pairs_file, script_dir)
        if not pairs_file.exists():
            raise SystemExit(f"Pairs file not found: {pairs_file}")
        args.pairs_file = str(pairs_file)

    output_json = resolve_path(args.output_json, script_dir)
    output_json.parent.mkdir(parents=True, exist_ok=True)

    weights = ObjectiveWeights(
        failure_weight=float(args.failure_weight),
        time_mismatch_weight=float(args.time_mismatch_weight),
        distance_mismatch_weight=float(args.distance_mismatch_weight),
        missing_ratio_penalty=float(args.missing_ratio_penalty),
        failed_run_penalty=float(args.failed_run_penalty),
    )

    candidates = build_candidates(speed_factors=speed_factors, segment_delays=segment_delays)
    print(f"Calibration candidates: {len(candidates)}")
    print(f"Evaluation script: {eval_script}")

    if args.dry_run:
        for candidate in candidates:
            print(f"  - {candidate.index:03d}: {candidate.label}")
        print("Dry run complete. No subprocesses were executed.")
        return

    keep_artifacts = bool(args.artifacts_dir)
    if keep_artifacts:
        artifacts_dir = resolve_path(args.artifacts_dir, script_dir)
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        context = nullcontext(artifacts_dir)
    else:
        context = TemporaryDirectory(prefix="motomap_calibration_", dir=str(script_dir))

    results: list[dict[str, Any]] = []
    started_at = datetime.now(timezone.utc).isoformat()

    with context as run_dir_ref:
        run_dir = Path(run_dir_ref)
        for candidate in candidates:
            print(f"[{candidate.index}/{len(candidates)}] Running {candidate.label}")
            result = run_candidate(
                candidate=candidate,
                eval_script=eval_script,
                script_dir=script_dir,
                args=args,
                run_dir=run_dir,
                keep_artifacts=keep_artifacts,
                weights=weights,
            )
            results.append(result)
            print(
                f"    status={result['status']} objective={result['objective_score']:.4f} "
                f"duration={result['duration_s']}s"
            )

    best = select_best_result(results)
    successful_count = sum(1 for result in results if result.get("status") == "ok")

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "started_at": started_at,
        "mode": "no_real_rider_data_calibration",
        "objective": {
            "formula": (
                "failure_weight * failure_ratio + "
                "time_mismatch_weight * avg_abs(1 - std_time_ratio_vs_baseline) + "
                "distance_mismatch_weight * avg_abs(1 - std_distance_ratio_vs_baseline)"
            ),
            "weights": {
                "failure_weight": weights.failure_weight,
                "time_mismatch_weight": weights.time_mismatch_weight,
                "distance_mismatch_weight": weights.distance_mismatch_weight,
            },
            "missing_ratio_penalty": weights.missing_ratio_penalty,
            "failed_run_penalty": weights.failed_run_penalty,
        },
        "evaluation_config": {
            "evaluation_script": str(eval_script),
            "batch": args.batch,
            "pairs_file": str(pairs_file) if pairs_file else None,
            "place": args.place,
            "seed": args.seed,
            "min_distance_m": args.min_distance_m,
            "max_distance_m": args.max_distance_m,
            "backend": args.backend,
            "valhalla_url": args.valhalla_url,
            "timeout_s": args.timeout_s,
        },
        "candidate_grid": {
            "speed_factors": speed_factors,
            "segment_delays_s": segment_delays,
            "count": len(candidates),
        },
        "successful_candidates": successful_count,
        "best_candidate": best,
        "results": results,
    }

    output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Saved calibration report: {output_json}")
    if best:
        print(
            "Best candidate -> "
            f"speed_factor={best['speed_factor']}, "
            f"segment_delay_s={best['segment_delay_s']}, "
            f"objective={best['objective_score']:.4f}"
        )
    else:
        print("No best candidate could be selected.")


if __name__ == "__main__":
    main()
