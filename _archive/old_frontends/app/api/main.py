"""MOTOMAP REST API — wraps the motomap Python library."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from api.demo_route import DEMO_ROUTE

ROUTE_FILE = (
    Path(__file__).resolve().parent.parent
    / "website"
    / "public"
    / "routes"
    / "motomap_route.json"
)

app = FastAPI(title="MOTOMAP API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "MOTOMAP API"}


@app.get("/api/route")
def get_route():
    if ROUTE_FILE.exists():
        try:
            with ROUTE_FILE.open(encoding="utf-8") as f:
                data = json.load(f)
            return data
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Route file read error: {exc}")
    return DEMO_ROUTE


@app.get("/api/route/info")
def get_route_info():
    has_real_data = ROUTE_FILE.exists()
    return {
        "has_real_data": has_real_data,
        "source": "generated" if has_real_data else "demo",
        "note": "Run website/generate_route.py with GOOGLE_MAPS_API_KEY to get real route data.",
    }
