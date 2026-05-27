"""
Stage-0 API: serves the landing page and exposes the deterministic engine.

  GET  /              -> the landing page (static)
  POST /api/match     -> full 36-point Ashtakoota Gun Milan from two birth details
  POST /api/chart     -> a single sidereal birth chart
  POST /api/lead      -> capture an email (the smoke-test conversion event)

The engine is deterministic and citable. Interpretation (the cited AI layer) is
NOT here yet — Stage 0 validates demand for the *score + report*, not the prose.
"""

from __future__ import annotations

import json
import pathlib
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ephemeris import compute_chart
from ashtakoota import gun_milan
from numerology import numerology_profile

WEB_DIR = pathlib.Path(__file__).resolve().parent.parent / "web"
LEADS_FILE = pathlib.Path(__file__).resolve().parent / "leads.jsonl"

app = FastAPI(title="Darpan Engine (Stage 0)")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)


class Person(BaseModel):
    name: str = ""
    year: int
    month: int
    day: int
    hour: int = 12
    minute: int = 0
    tz_offset: float = 0.0
    latitude: float = 0.0
    longitude: float = 0.0


class MatchRequest(BaseModel):
    boy: Person
    girl: Person


class Lead(BaseModel):
    email: str
    context: str = ""


def _chart(p: Person):
    return compute_chart(
        p.year, p.month, p.day, p.hour + p.minute / 60.0,
        p.tz_offset, p.latitude, p.longitude,
    )


def _moon_summary(chart) -> dict:
    m = chart.planet("Moon")
    return {
        "moon_sign": m.sign,
        "moon_nakshatra": m.nakshatra,
        "moon_pada": m.pada,
        "ascendant_sign": chart.ascendant.sign,
    }


@app.post("/api/chart")
def chart_endpoint(p: Person):
    return _chart(p).to_dict()


@app.post("/api/match")
def match_endpoint(req: MatchRequest):
    boy_chart, girl_chart = _chart(req.boy), _chart(req.girl)
    boy_moon, girl_moon = boy_chart.planet("Moon"), girl_chart.planet("Moon")
    result = gun_milan(
        boy_moon.nakshatra_index, boy_moon.sign_index,
        girl_moon.nakshatra_index, girl_moon.sign_index,
    )
    return {
        "gun_milan": result,
        "boy": _moon_summary(boy_chart),
        "girl": _moon_summary(girl_chart),
        "method": "Ashtakoota (8-koota, 36-point) on Lahiri sidereal Moon positions",
    }


@app.post("/api/numerology")
def numerology_endpoint(p: Person):
    return numerology_profile(p.name, p.day, p.month, p.year)


@app.post("/api/lead")
def lead_endpoint(lead: Lead):
    record = {"email": lead.email, "context": lead.context,
              "ts": datetime.now(timezone.utc).isoformat()}
    with LEADS_FILE.open("a") as f:
        f.write(json.dumps(record) + "\n")
    return {"ok": True}


if WEB_DIR.exists():
    app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="web")
