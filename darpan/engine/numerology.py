"""
Numerology — deterministic arithmetic. Chaldean (popular in India) + Pythagorean
name numbers, plus the core date-derived numbers. No interpretation here.
"""

from __future__ import annotations

_PYTHAGOREAN = {  # A=1..I=9, repeating
    **{c: (i % 9) + 1 for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ")},
}
_CHALDEAN = {
    "A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 8, "G": 3, "H": 5, "I": 1,
    "J": 1, "K": 2, "L": 3, "M": 4, "N": 5, "O": 7, "P": 8, "Q": 1, "R": 2,
    "S": 3, "T": 4, "U": 6, "V": 6, "W": 6, "X": 5, "Y": 1, "Z": 7,
}


def _reduce(n: int, keep_master: bool = True) -> int:
    while n > 9:
        if keep_master and n in (11, 22, 33):
            return n
        n = sum(int(d) for d in str(n))
    return n


def _name_number(name: str, table: dict[str, int]) -> int:
    total = sum(table.get(c, 0) for c in name.upper() if c.isalpha())
    return _reduce(total)


def numerology_profile(name: str, day: int, month: int, year: int) -> dict:
    """Driver (birth day), Destiny/Life-Path (full DOB), and name numbers."""
    driver = _reduce(day, keep_master=False)
    destiny = _reduce(sum(int(d) for d in f"{day}{month}{year}"))
    return {
        "driver_number": driver,
        "destiny_number": destiny,
        "name_number_chaldean": _name_number(name, _CHALDEAN),
        "name_number_pythagorean": _name_number(name, _PYTHAGOREAN),
    }
