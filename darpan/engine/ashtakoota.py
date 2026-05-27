"""
Ashtakoota Gun Milan — the classical 36-point Vedic marriage-compatibility match.

Eight kootas, computed deterministically from each partner's Moon nakshatra and
Moon sign (rashi):

    Varna 1 | Vashya 2 | Tara 3 | Yoni 4 | Graha Maitri 5 | Gana 6 | Bhakoot 7 | Nadi 8
    => maximum 36.

Each koota returns its score AND a short method note (the rule applied), so the
interpretation layer can cite exactly how a number was derived. The high-weight
kootas (Nadi, Bhakoot, Gana, Graha Maitri) use exact, well-established rules.
Yoni and Vashya follow the standard method with documented simplifications where
classical sources carry regional variants.
"""

from __future__ import annotations

from dataclasses import dataclass

# --- Nadi (8): nakshatra -> 0 Aadi(Vata) | 1 Madhya(Pitta) | 2 Antya(Kapha) ---
NADI = {
    0: 0, 5: 0, 6: 0, 11: 0, 12: 0, 17: 0, 18: 0, 23: 0, 24: 0,   # Aadi
    1: 1, 4: 1, 7: 1, 10: 1, 13: 1, 16: 1, 19: 1, 22: 1, 25: 1,   # Madhya
    2: 2, 3: 2, 8: 2, 9: 2, 14: 2, 15: 2, 20: 2, 21: 2, 26: 2,    # Antya
}

# --- Gana (6): nakshatra -> 0 Deva | 1 Manushya | 2 Rakshasa ---
GANA = {
    0: 0, 4: 0, 6: 0, 7: 0, 12: 0, 14: 0, 16: 0, 21: 0, 26: 0,    # Deva
    1: 1, 3: 1, 5: 1, 10: 1, 11: 1, 19: 1, 20: 1, 24: 1, 25: 1,   # Manushya
    2: 2, 8: 2, 9: 2, 13: 2, 15: 2, 17: 2, 18: 2, 22: 2, 23: 2,   # Rakshasa
}
# Gana points [boy][girl]
_GANA_PTS = [[6, 6, 1], [5, 6, 0], [1, 0, 6]]

# --- Yoni (4): nakshatra -> animal index (14 yonis) ---
YONI = {
    0: 0, 23: 0,    # Horse
    1: 1, 26: 1,    # Elephant
    2: 2, 7: 2,     # Sheep
    3: 3, 4: 3,     # Serpent
    5: 4, 18: 4,    # Dog
    6: 5, 8: 5,     # Cat
    9: 6, 10: 6,    # Rat
    11: 7, 25: 7,   # Cow
    12: 8, 14: 8,   # Buffalo
    13: 9, 15: 9,   # Tiger
    16: 10, 17: 10, # Deer
    19: 11, 21: 11, # Monkey
    20: 12,         # Mongoose
    22: 13, 24: 13, # Lion
}
_YONI_ENEMIES = {
    frozenset((7, 9)), frozenset((1, 13)), frozenset((0, 8)),
    frozenset((4, 10)), frozenset((3, 12)), frozenset((5, 6)),
    frozenset((11, 2)),
}

# --- Varna (1): rashi -> rank (4 Brahmin .. 1 Shudra) ---
VARNA = {3: 4, 7: 4, 11: 4, 0: 3, 4: 3, 8: 3, 1: 2, 5: 2, 9: 2, 2: 1, 6: 1, 10: 1}

# --- Vashya (2): rashi -> group 0 Nara|1 Chatushpada|2 Jalachara|3 Vanachara|4 Keeta ---
VASHYA = {0: 1, 1: 1, 2: 0, 3: 2, 4: 3, 5: 0, 6: 0, 7: 4, 8: 0, 9: 2, 10: 0, 11: 2}
_VASHYA_PTS = [
    [2, 1, 1, 0, 1],
    [0, 2, 1, 1, 1],
    [1, 1, 2, 1, 0.5],
    [1, 0, 1, 2, 1],
    [1, 1, 1, 1, 2],
]

# --- Graha Maitri (5): rashi lords + natural planetary friendship ---
RASHI_LORD = {
    0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon", 4: "Sun", 5: "Mercury",
    6: "Venus", 7: "Mars", 8: "Jupiter", 9: "Saturn", 10: "Saturn", 11: "Jupiter",
}
_FRIENDS = {
    "Sun": {"Moon", "Mars", "Jupiter"},
    "Moon": {"Sun", "Mercury"},
    "Mars": {"Sun", "Moon", "Jupiter"},
    "Mercury": {"Sun", "Venus"},
    "Jupiter": {"Sun", "Moon", "Mars"},
    "Venus": {"Mercury", "Saturn"},
    "Saturn": {"Mercury", "Venus"},
}
_ENEMIES = {
    "Sun": {"Venus", "Saturn"},
    "Moon": set(),
    "Mars": {"Mercury"},
    "Mercury": {"Moon"},
    "Jupiter": {"Mercury", "Venus"},
    "Venus": {"Sun", "Moon"},
    "Saturn": {"Sun", "Moon", "Mars"},
}

_INAUSPICIOUS_TARA = {3, 5, 7}  # Vipat, Pratyak, Vadha


@dataclass
class KootaResult:
    name: str
    score: float
    max: float
    note: str


def _relation(a: str, b: str) -> str:
    if a == b or b in _FRIENDS[a]:
        return "F"
    if b in _ENEMIES[a]:
        return "E"
    return "N"


def _varna(boy_rashi: int, girl_rashi: int) -> KootaResult:
    b, g = VARNA[boy_rashi], VARNA[girl_rashi]
    score = 1.0 if b >= g else 0.0
    return KootaResult("Varna", score, 1, f"boy rank {b} {'>=' if score else '<'} girl rank {g}")


def _vashya(boy_rashi: int, girl_rashi: int) -> KootaResult:
    score = _VASHYA_PTS[VASHYA[boy_rashi]][VASHYA[girl_rashi]]
    return KootaResult("Vashya", float(score), 2, "standard vashya group matrix")


def _tara(boy_nak: int, girl_nak: int) -> KootaResult:
    def side(frm: int, to: int) -> bool:
        count = ((to - frm) % 27) + 1
        rem = count % 9
        if rem == 0:
            rem = 9
        return rem not in _INAUSPICIOUS_TARA
    good = (1.5 if side(boy_nak, girl_nak) else 0.0) + (1.5 if side(girl_nak, boy_nak) else 0.0)
    return KootaResult("Tara", good, 3, "9-count both ways; Vipat/Pratyak/Vadha inauspicious")


def _yoni(boy_nak: int, girl_nak: int) -> KootaResult:
    yb, yg = YONI[boy_nak], YONI[girl_nak]
    if yb == yg:
        score = 4.0
    elif frozenset((yb, yg)) in _YONI_ENEMIES:
        score = 0.0
    else:
        score = 2.0
    return KootaResult("Yoni", score, 4, "same yoni=4, sworn-enemy=0, else neutral=2")


def _graha_maitri(boy_rashi: int, girl_rashi: int) -> KootaResult:
    lb, lg = RASHI_LORD[boy_rashi], RASHI_LORD[girl_rashi]
    r1, r2 = _relation(lb, lg), _relation(lg, lb)
    pair = {r1, r2}
    if pair == {"F"}:
        score = 5.0
    elif pair == {"F", "N"}:
        score = 4.0
    elif pair == {"N"}:
        score = 3.0
    elif pair == {"F", "E"}:
        score = 1.0
    elif pair == {"N", "E"}:
        score = 0.5
    else:
        score = 0.0
    return KootaResult("Graha Maitri", score, 5, f"lords {lb}/{lg}; relation {r1}/{r2}")


def _gana(boy_nak: int, girl_nak: int) -> KootaResult:
    score = _GANA_PTS[GANA[boy_nak]][GANA[girl_nak]]
    return KootaResult("Gana", float(score), 6, "Deva/Manushya/Rakshasa temperament matrix")


def _bhakoot(boy_rashi: int, girl_rashi: int) -> KootaResult:
    p1 = ((girl_rashi - boy_rashi) % 12) + 1
    p2 = ((boy_rashi - girl_rashi) % 12) + 1
    dosha = {p1, p2} in ({6, 8}, {5, 9}, {2, 12})
    return KootaResult("Bhakoot", 0.0 if dosha else 7.0, 7,
                       f"mutual rashi positions {p1}/{p2}" + (" (dosha)" if dosha else ""))


def _nadi(boy_nak: int, girl_nak: int) -> KootaResult:
    same = NADI[boy_nak] == NADI[girl_nak]
    return KootaResult("Nadi", 0.0 if same else 8.0, 8,
                       "same nadi = dosha (0)" if same else "different nadi")


def _band(total: float) -> str:
    if total >= 32:
        return "Uttam (excellent)"
    if total >= 24:
        return "Madhyam (good)"
    if total >= 18:
        return "passable (above the conventional 18 threshold)"
    return "below the conventional 18 threshold"


def gun_milan(boy_nak: int, boy_rashi: int, girl_nak: int, girl_rashi: int) -> dict:
    """Compute the full 36-point Ashtakoota match from each partner's Moon
    nakshatra index (0..26) and Moon sign index (0..11)."""
    kootas = [
        _varna(boy_rashi, girl_rashi),
        _vashya(boy_rashi, girl_rashi),
        _tara(boy_nak, girl_nak),
        _yoni(boy_nak, girl_nak),
        _graha_maitri(boy_rashi, girl_rashi),
        _gana(boy_nak, girl_nak),
        _bhakoot(boy_rashi, girl_rashi),
        _nadi(boy_nak, girl_nak),
    ]
    total = sum(k.score for k in kootas)
    return {
        "total": round(total, 1),
        "max": 36,
        "band": _band(total),
        "nadi_dosha": kootas[7].score == 0,
        "bhakoot_dosha": kootas[6].score == 0,
        "kootas": [k.__dict__ for k in kootas],
    }
