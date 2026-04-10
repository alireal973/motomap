import json
from pathlib import Path
from unittest.mock import mock_open, patch

from api.services.route_preview import DEMO_ROUTE, RoutePreviewService


def test_route_preview_falls_back_to_demo_payload():
    service = RoutePreviewService(repo_root=Path("C:/repo"))

    payload = service.get_route_payload()
    info = service.get_route_info()

    assert payload == DEMO_ROUTE
    assert info["has_real_data"] is False
    assert info["source"] == "demo"
    assert info["path"] is None


def test_route_preview_prefers_generated_website_payload():
    repo_root = Path("C:/repo")
    route_path = repo_root / "website" / "routes" / "motomap_route.json"
    payload = {
        "origin": {"lat": 1.0, "lng": 2.0},
        "destination": {"lat": 3.0, "lng": 4.0},
        "origin_label": "A",
        "destination_label": "B",
        "google_route": [],
        "google_stats": {
            "mesafe_m": 1000,
            "sure_s": 120,
            "mesafe_text": "1 km",
            "sure_text": "2 dk",
        },
        "modes": {},
    }
    service = RoutePreviewService(repo_root=repo_root)

    with patch.object(RoutePreviewService, "get_generated_route_path", return_value=route_path):
        with patch.object(Path, "open", mock_open(read_data=json.dumps(payload))):
            info = service.get_route_info()
            assert service.get_route_payload() == payload

    assert info["has_real_data"] is True
    assert info["source"] == "generated"
    assert info["path"] == "website/routes/motomap_route.json"


def test_route_preview_supports_legacy_app_generated_path(monkeypatch):
    repo_root = Path("C:/repo")
    legacy_path = repo_root / "app" / "website" / "public" / "routes" / "motomap_route.json"
    service = RoutePreviewService(repo_root=repo_root)

    def fake_exists(self: Path) -> bool:
        return self == legacy_path

    monkeypatch.setattr(Path, "exists", fake_exists)

    assert service.get_generated_route_path() == legacy_path
