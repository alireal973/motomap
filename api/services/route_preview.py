"""Canonical route preview payload service.

This keeps `/api/route` on the main backend while the live route-generation
API is being integrated. It prefers generated route JSON when available and
falls back to a bundled demo payload otherwise.
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

DEMO_ROUTE: dict[str, Any] = {
    "origin": {"lat": 40.9923, "lng": 29.0239},
    "destination": {"lat": 40.9700, "lng": 29.0380},
    "origin_label": "Kadikoy Iskele",
    "destination_label": "Kalamis Parki",
    "google_route": [
        {"lat": 40.9923, "lng": 29.0239},
        {"lat": 40.9915, "lng": 29.0260},
        {"lat": 40.9905, "lng": 29.0280},
        {"lat": 40.9890, "lng": 29.0295},
        {"lat": 40.9875, "lng": 29.0305},
        {"lat": 40.9860, "lng": 29.0315},
        {"lat": 40.9840, "lng": 29.0330},
        {"lat": 40.9820, "lng": 29.0345},
        {"lat": 40.9800, "lng": 29.0360},
        {"lat": 40.9780, "lng": 29.0368},
        {"lat": 40.9760, "lng": 29.0372},
        {"lat": 40.9740, "lng": 29.0376},
        {"lat": 40.9720, "lng": 29.0378},
        {"lat": 40.9700, "lng": 29.0380},
    ],
    "google_stats": {
        "mesafe_m": 2850,
        "mesafe_text": "2.9 km",
        "sure_s": 540,
        "sure_text": "9 dk",
    },
    "modes": {
        "standart": {
            "coordinates": [
                {"lat": 40.9923, "lng": 29.0239},
                {"lat": 40.9912, "lng": 29.0252},
                {"lat": 40.9900, "lng": 29.0268},
                {"lat": 40.9888, "lng": 29.0282},
                {"lat": 40.9875, "lng": 29.0298},
                {"lat": 40.9860, "lng": 29.0310},
                {"lat": 40.9845, "lng": 29.0322},
                {"lat": 40.9828, "lng": 29.0335},
                {"lat": 40.9810, "lng": 29.0348},
                {"lat": 40.9790, "lng": 29.0358},
                {"lat": 40.9770, "lng": 29.0366},
                {"lat": 40.9748, "lng": 29.0372},
                {"lat": 40.9724, "lng": 29.0377},
                {"lat": 40.9700, "lng": 29.0380},
            ],
            "stats": {
                "mesafe_m": 2780,
                "sure_s": 420,
                "viraj_fun": 4,
                "viraj_tehlike": 1,
                "yuksek_risk": 0,
                "serit_paylasimi": 1200,
                "ortalama_egim": 0.018,
                "ucretli": False,
            },
        },
        "viraj_keyfi": {
            "coordinates": [
                {"lat": 40.9923, "lng": 29.0239},
                {"lat": 40.9915, "lng": 29.0248},
                {"lat": 40.9905, "lng": 29.0255},
                {"lat": 40.9895, "lng": 29.0265},
                {"lat": 40.9882, "lng": 29.0278},
                {"lat": 40.9868, "lng": 29.0292},
                {"lat": 40.9852, "lng": 29.0305},
                {"lat": 40.9835, "lng": 29.0318},
                {"lat": 40.9818, "lng": 29.0330},
                {"lat": 40.9800, "lng": 29.0342},
                {"lat": 40.9780, "lng": 29.0352},
                {"lat": 40.9760, "lng": 29.0362},
                {"lat": 40.9738, "lng": 29.0370},
                {"lat": 40.9718, "lng": 29.0376},
                {"lat": 40.9700, "lng": 29.0380},
            ],
            "stats": {
                "mesafe_m": 3100,
                "sure_s": 510,
                "viraj_fun": 11,
                "viraj_tehlike": 2,
                "yuksek_risk": 0,
                "serit_paylasimi": 1200,
                "ortalama_egim": 0.024,
                "ucretli": False,
            },
        },
        "guvenli": {
            "coordinates": [
                {"lat": 40.9923, "lng": 29.0239},
                {"lat": 40.9910, "lng": 29.0258},
                {"lat": 40.9895, "lng": 29.0274},
                {"lat": 40.9878, "lng": 29.0288},
                {"lat": 40.9862, "lng": 29.0302},
                {"lat": 40.9845, "lng": 29.0316},
                {"lat": 40.9825, "lng": 29.0328},
                {"lat": 40.9805, "lng": 29.0340},
                {"lat": 40.9784, "lng": 29.0350},
                {"lat": 40.9762, "lng": 29.0360},
                {"lat": 40.9740, "lng": 29.0368},
                {"lat": 40.9720, "lng": 29.0374},
                {"lat": 40.9700, "lng": 29.0380},
            ],
            "stats": {
                "mesafe_m": 2680,
                "sure_s": 480,
                "viraj_fun": 2,
                "viraj_tehlike": 0,
                "yuksek_risk": 0,
                "serit_paylasimi": 1200,
                "ortalama_egim": 0.012,
                "ucretli": False,
            },
        },
    },
}


class RoutePreviewService:
    """Serve the canonical route preview payload from the main backend."""

    def __init__(self, repo_root: Path | None = None):
        self.repo_root = repo_root or Path(__file__).resolve().parents[2]

    def iter_candidate_paths(self) -> tuple[Path, ...]:
        return (
            self.repo_root / "website" / "routes" / "motomap_route.json",
            self.repo_root / "website" / "public" / "routes" / "motomap_route.json",
            self.repo_root / "app" / "website" / "routes" / "motomap_route.json",
            self.repo_root / "app" / "website" / "public" / "routes" / "motomap_route.json",
        )

    def get_generated_route_path(self) -> Path | None:
        for candidate in self.iter_candidate_paths():
            if candidate.exists():
                return candidate
        return None

    def load_generated_route(self) -> dict[str, Any]:
        route_path = self.get_generated_route_path()
        if not route_path:
            raise FileNotFoundError("Generated route payload not found")

        with route_path.open(encoding="utf-8") as handle:
            return json.load(handle)

    def get_route_payload(self) -> dict[str, Any]:
        route_path = self.get_generated_route_path()
        if route_path:
            return self.load_generated_route()
        return deepcopy(DEMO_ROUTE)

    def get_route_info(self) -> dict[str, Any]:
        route_path = self.get_generated_route_path()
        relative_path = (
            route_path.relative_to(self.repo_root).as_posix()
            if route_path is not None
            else None
        )
        return {
            "has_real_data": route_path is not None,
            "source": "generated" if route_path is not None else "demo",
            "path": relative_path,
            "note": (
                "Run website/generate_route.py or app/website/generate_route.py "
                "to produce a generated route payload for compatibility mode."
            ),
        }
