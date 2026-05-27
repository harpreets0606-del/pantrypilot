"""Engine correctness checks. Run: `python test_engine.py` (no pytest needed)."""

from __future__ import annotations

from ephemeris import compute_chart, ayanamsa, julian_day_ut
from ashtakoota import gun_milan, NADI, GANA, YONI


def test_ayanamsa_j2000():
    # Lahiri ayanamsa at J2000.0 is ~23.85 degrees (well-established value).
    assert abs(ayanamsa(2451545.0) - 23.85) < 0.05


def test_mesha_sankranti_sun_in_sidereal_aries():
    # ~14 Apr the Sun enters sidereal Aries (Mesha Sankranti). Real-world check
    # that Lahiri sidereal longitudes are right: Sun should be early Aries.
    chart = compute_chart(2024, 4, 14, 12.0, 0.0, 0.0, 0.0)
    sun = chart.planet("Sun")
    assert sun.sign == "Aries", sun.sign
    assert sun.degree_in_sign < 3.0, sun.degree_in_sign


def test_tables_cover_27_nakshatras():
    for table in (NADI, GANA, YONI):
        assert set(table.keys()) == set(range(27))


def test_gun_milan_bounds_and_shape():
    res = gun_milan(3, 1, 10, 4)  # arbitrary valid indices
    assert 0 <= res["total"] <= 36
    assert len(res["kootas"]) == 8
    assert sum(k["max"] for k in res["kootas"]) == 36


def test_identical_moon_triggers_nadi_dosha():
    # Same nakshatra & rashi -> same Nadi -> Nadi dosha (0), no Bhakoot dosha.
    res = gun_milan(5, 2, 5, 2)
    assert res["nadi_dosha"] is True
    assert res["bhakoot_dosha"] is False
    nadi = next(k for k in res["kootas"] if k["name"] == "Nadi")
    assert nadi["score"] == 0
    # Varna1+Vashya2+Tara3+Yoni4+GrahaMaitri5+Gana6+Bhakoot7+Nadi0 = 28
    assert res["total"] == 28


def test_different_nadi_scores_eight():
    # Ashwini (nadi Aadi) vs Bharani (nadi Madhya) -> different nadi -> 8.
    res = gun_milan(0, 0, 1, 1)
    nadi = next(k for k in res["kootas"] if k["name"] == "Nadi")
    assert nadi["score"] == 8


def test_julian_day_tz_offset():
    # 06:00 at +5.5 == 00:30 UTC; sanity that tz shifts the JD correctly.
    jd_ist = julian_day_ut(2000, 1, 1, 6.0, 5.5)
    jd_utc = julian_day_ut(2000, 1, 1, 0.5, 0.0)
    assert abs(jd_ist - jd_utc) < 1e-6


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"PASS  {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL  {t.__name__}: {e}")
        except Exception as e:  # noqa: BLE001
            print(f"ERROR {t.__name__}: {type(e).__name__}: {e}")
    print(f"\n{passed}/{len(tests)} passed")
