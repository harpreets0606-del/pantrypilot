# Darpan — Stage 0 (smoke test + engine)

The validate-first slice: a **trust-first landing page** (the demand test) backed by a
**real deterministic Vedic engine** (kundli + the 36-point Ashtakoota Gun Milan match).
No AI interpretation yet — Stage 0 proves people want the *sourced match + report*
before we build the citation/AI layer.

## What's here
```
engine/   Python — Swiss Ephemeris (Lahiri sidereal) chart + Ashtakoota + numerology + API
web/      Static landing page that calls the engine for a live 36-point score
```

- `ephemeris.py` — exact sidereal positions, lagna, nakshatra (pyswisseph, Moshier, no data files).
- `ashtakoota.py` — the 8 kootas (36 points) with a per-koota method note for traceability.
- `numerology.py` — Chaldean + Pythagorean name/date numbers.
- `api.py` — serves the page + `/api/match`, `/api/chart`, `/api/numerology`, `/api/lead`.
- `test_engine.py` — correctness checks, incl. a real-world Mesha Sankranti astronomy check.

## Run it
```bash
cd engine
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python test_engine.py          # 7/7 should pass
uvicorn api:app --reload       # then open http://localhost:8000
```

CLI sanity check:
```bash
python cli.py match --boy 1990-08-15T10:30 +5.5 19.07 72.87 \
                    --girl 1992-03-22T14:15 +5.5 28.61 77.21
```

## Honest scope / notes
- **Deterministic only.** The engine computes; it does not interpret. The cited AI
  reading is the next slice.
- **High-weight kootas (Nadi, Bhakoot, Gana, Graha Maitri) use exact classical rules.**
  Yoni and Vashya follow the standard method with documented simplifications where
  sources carry regional variants (see comments in `ashtakoota.py`).
- **Timezone/DST is simplified** to a fixed offset per city in the demo; the full engine
  resolves historical TZ/DST precisely.
- `leads.jsonl` (gitignored) is a placeholder capture; for a live smoke test, point the
  form at a real form/analytics service and measure click→submit conversion.
