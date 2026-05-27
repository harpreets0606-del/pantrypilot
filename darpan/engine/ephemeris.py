"""
Deterministic Vedic chart computation via Swiss Ephemeris.

This module does PURE ASTRONOMY — no AI, no interpretation. Given an exact
birth moment + place it returns sidereal (Lahiri) planetary positions, the
ascendant, and each planet's sign + nakshatra. Reproducible to the arc-second.

Uses the built-in Moshier ephemeris (FLG_MOSEPH) so no external data files are
required. Default ayanamsa is Lahiri / Chitrapaksha — India's official standard
(adopted 1956 by the Calendar Reform Committee).
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
import swisseph as swe

# 27 nakshatras (lunar mansions), in order from 0deg sidereal Aries.
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha",
    "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
    "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

RASHIS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Swiss Ephemeris planet ids we compute. Rahu = Mean lunar node; Ketu = +180.
_PLANETS = [
    ("Sun", swe.SUN),
    ("Moon", swe.MOON),
    ("Mars", swe.MARS),
    ("Mercury", swe.MERCURY),
    ("Jupiter", swe.JUPITER),
    ("Venus", swe.VENUS),
    ("Saturn", swe.SATURN),
    ("Rahu", swe.MEAN_NODE),
]

_NAK_SPAN = 360.0 / 27.0  # 13deg 20'
_PADA_SPAN = _NAK_SPAN / 4.0
_FLAGS = swe.FLG_MOSEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED


def _init() -> None:
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)


def julian_day_ut(year: int, month: int, day: int, hour: float, tz_offset: float) -> float:
    """Julian Day in UT. `hour` is local clock time (e.g. 14.5 = 14:30);
    `tz_offset` is hours east of UTC (e.g. +5.5 for IST, -5 for US EST)."""
    ut_hour = hour - tz_offset
    return swe.julday(year, month, day, ut_hour, swe.GREG_CAL)


@dataclass
class Position:
    name: str
    longitude: float       # sidereal ecliptic longitude, 0-360
    sign_index: int        # 0=Aries .. 11=Pisces
    sign: str
    degree_in_sign: float
    nakshatra_index: int   # 0..26
    nakshatra: str
    pada: int              # 1..4
    retrograde: bool


def _describe(name: str, lon: float, speed: float = 0.0) -> Position:
    lon = lon % 360.0
    sign_index = int(lon // 30)
    nak_index = int(lon // _NAK_SPAN)
    pada = int((lon % _NAK_SPAN) // _PADA_SPAN) + 1
    return Position(
        name=name,
        longitude=round(lon, 4),
        sign_index=sign_index,
        sign=RASHIS[sign_index],
        degree_in_sign=round(lon - sign_index * 30, 4),
        nakshatra_index=nak_index,
        nakshatra=NAKSHATRAS[nak_index],
        pada=pada,
        retrograde=speed < 0,
    )


@dataclass
class Chart:
    julian_day: float
    ascendant: Position
    planets: list[Position]

    def planet(self, name: str) -> Position:
        for p in self.planets:
            if p.name == name:
                return p
        raise KeyError(name)

    def to_dict(self) -> dict:
        return {
            "julian_day": self.julian_day,
            "ascendant": asdict(self.ascendant),
            "planets": [asdict(p) for p in self.planets],
        }


def compute_chart(
    year: int, month: int, day: int, hour: float,
    tz_offset: float, latitude: float, longitude: float,
) -> Chart:
    """Compute a sidereal (Lahiri) birth chart. `hour` is local clock time."""
    _init()
    jd = julian_day_ut(year, month, day, hour, tz_offset)

    positions: list[Position] = []
    for name, pid in _PLANETS:
        xx, _ = swe.calc_ut(jd, pid, _FLAGS)
        positions.append(_describe(name, xx[0], xx[3]))
    rahu = next(p for p in positions if p.name == "Rahu")
    positions.append(_describe("Ketu", rahu.longitude + 180.0))

    # Whole-sign houses ('W'); ascmc[0] is the sidereal ascendant.
    _, ascmc = swe.houses_ex(jd, latitude, longitude, b"W", swe.FLG_SIDEREAL)
    ascendant = _describe("Ascendant", ascmc[0])

    return Chart(julian_day=jd, ascendant=ascendant, planets=positions)


def ayanamsa(jd: float) -> float:
    """Lahiri ayanamsa (degrees) for a given Julian Day — for verification."""
    _init()
    return swe.get_ayanamsa_ut(jd)
