"""Helpers for multi-case website comparison suites."""

from __future__ import annotations

from datetime import datetime, timezone

MODES = ("standart", "viraj_keyfi", "guvenli")

DEFAULT_CASE_DEFINITIONS = [
    {
        "case_id": "moda_kalamis",
        "label": "Moda Iskele -> Kalamis Parki",
        "origin_label": "Moda Iskele",
        "destination_label": "Kalamis Parki",
        "origin": {"lat": 40.9889, "lng": 29.0242},
        "destination": {"lat": 40.9700, "lng": 29.0380},
    },
    {
        "case_id": "hasanpasa_caddebostan",
        "label": "Hasanpasa -> Caddebostan Sahil",
        "origin_label": "Hasanpasa",
        "destination_label": "Caddebostan Sahil",
        "origin": {"lat": 40.9907, "lng": 29.0452},
        "destination": {"lat": 40.9627, "lng": 29.0639},
    },
    {
        "case_id": "bostanci_fenerbahce",
        "label": "Bostanci Iskele -> Fenerbahce Parki",
        "origin_label": "Bostanci Iskele",
        "destination_label": "Fenerbahce Parki",
        "origin": {"lat": 40.9524, "lng": 29.0943},
        "destination": {"lat": 40.9767, "lng": 29.0423},
    },
]


def safe_ratio(
    numerator: float | int | None, denominator: float | int | None
) -> float | None:
    if numerator is None or denominator is None:
        return None
    denom = float(denominator)
    if denom <= 0:
        return None
    return float(numerator) / denom


def build_mode_comparisons(route_doc: dict) -> dict[str, dict[str, float | int | None]]:
    baseline_stats = route_doc.get("baseline_stats", {}) or route_doc.get(
        "google_stats", {}
    )
    modes = route_doc.get("modes", {})
    standard_stats = (modes.get("standart") or {}).get("stats", {})
    comparisons: dict[str, dict[str, float | int | None]] = {}

    for mode in MODES:
        stats = (modes.get(mode) or {}).get("stats", {})
        comparisons[mode] = {
            "distance_ratio_vs_baseline": safe_ratio(
                stats.get("mesafe_m"), baseline_stats.get("mesafe_m")
            ),
            "time_ratio_vs_baseline": safe_ratio(
                stats.get("sure_s"), baseline_stats.get("sure_s")
            ),
            "fun_delta_vs_standard": (
                int(stats.get("viraj_fun", 0)) - int(standard_stats.get("viraj_fun", 0))
                if stats
                else None
            ),
            "risk_delta_vs_standard": (
                int(stats.get("yuksek_risk", 0))
                - int(standard_stats.get("yuksek_risk", 0))
                if stats
                else None
            ),
        }
    return comparisons


def build_case_evidence(route_doc: dict) -> dict:
    modes = route_doc.get("modes", {})
    baseline_route = route_doc.get("baseline_route", []) or route_doc.get(
        "google_route", []
    )
    baseline_stats = route_doc.get("baseline_stats", {}) or route_doc.get(
        "google_stats", {}
    )
    comparisons = build_mode_comparisons(route_doc)

    standard_stats = (modes.get("standart") or {}).get("stats", {})
    viraj_stats = (modes.get("viraj_keyfi") or {}).get("stats", {})
    safe_stats = (modes.get("guvenli") or {}).get("stats", {})

    checks = {
        "baseline_route_exists": len(baseline_route) > 0,
        "all_modes_exist": all(
            len((modes.get(mode) or {}).get("coordinates", [])) > 0 for mode in MODES
        ),
        "viraj_fun_ge_standard": int(viraj_stats.get("viraj_fun", -1))
        >= int(standard_stats.get("viraj_fun", 10**9)),
        "guvenli_risk_le_standard": int(safe_stats.get("yuksek_risk", 10**9))
        <= int(standard_stats.get("yuksek_risk", -1)),
        "standart_distance_close_to_baseline": (
            comparisons["standart"]["distance_ratio_vs_baseline"] is not None
            and 0.7
            <= float(comparisons["standart"]["distance_ratio_vs_baseline"])
            <= 1.4
        ),
        "standart_time_close_to_baseline": (
            comparisons["standart"]["time_ratio_vs_baseline"] is not None
            and 0.5
            <= float(comparisons["standart"]["time_ratio_vs_baseline"])
            <= 1.8
        ),
    }

    pass_count = sum(1 for value in checks.values() if value)
    total = len(checks)
    verdict = "PASS" if pass_count == total else "FAIL"

    return {
        "checks": checks,
        "score": pass_count,
        "total": total,
        "verdict": verdict,
        "baseline_backend": route_doc.get("baseline_backend", "google"),
        "mode_comparisons": comparisons,
    }


def build_suite_summary(cases: list[dict]) -> dict:
    total_cases = len(cases)
    total_mode_routes = total_cases * len(MODES)
    passed_cases = 0
    total_score = 0
    total_possible = 0

    for case in cases:
        evidence = case.get("evidence", {})
        score = int(evidence.get("score", 0))
        possible = int(evidence.get("total", 0))
        total_score += score
        total_possible += possible
        if evidence.get("verdict") == "PASS":
            passed_cases += 1

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_cases": total_cases,
        "total_mode_routes": total_mode_routes,
        "passed_cases": passed_cases,
        "failed_cases": total_cases - passed_cases,
        "average_score_ratio": (
            round(total_score / total_possible, 4) if total_possible else None
        ),
    }
