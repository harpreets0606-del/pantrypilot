"""Quick CLI to sanity-check the engine, e.g.:

    python cli.py match \
      --boy   1990-08-15T10:30 +5.5 19.07 72.87 \
      --girl  1992-03-22T14:15 +5.5 28.61 77.21
"""

from __future__ import annotations

import argparse
import json

from ephemeris import compute_chart
from ashtakoota import gun_milan


def _parse_person(dt: str, tz: str, lat: str, lon: str):
    date_part, time_part = dt.split("T")
    y, m, d = (int(x) for x in date_part.split("-"))
    hh, mm = (int(x) for x in time_part.split(":"))
    return compute_chart(y, m, d, hh + mm / 60.0, float(tz), float(lat), float(lon))


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    mp = sub.add_parser("match")
    mp.add_argument("--boy", nargs=4, metavar=("DT", "TZ", "LAT", "LON"), required=True)
    mp.add_argument("--girl", nargs=4, metavar=("DT", "TZ", "LAT", "LON"), required=True)
    args = ap.parse_args()

    if args.cmd == "match":
        boy = _parse_person(*args.boy)
        girl = _parse_person(*args.girl)
        bm, gm = boy.planet("Moon"), girl.planet("Moon")
        result = gun_milan(bm.nakshatra_index, bm.sign_index,
                           gm.nakshatra_index, gm.sign_index)
        print(json.dumps({
            "boy_moon": f"{bm.nakshatra} / {bm.sign}",
            "girl_moon": f"{gm.nakshatra} / {gm.sign}",
            "result": result,
        }, indent=2))


if __name__ == "__main__":
    main()
