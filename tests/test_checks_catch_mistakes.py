"""Checks on the checks.

A test suite that only ever sees the right answer proves nothing. These assert
that the tolerances in test_bracket.py reject plausible wrong parts - the kind a
solver produces when it reads the spec carelessly, not absurd ones.
"""

import math

import pytest

from test_bracket import (
    BASE_HOLES,
    BASE_HOLE_R,
    FLANGE_HOLES,
    PLATE_T,
    PROBE_GAP,
    V_EXPECTED,
    V_FILLET,
    VOL_TOL,
    material_at,
    shape,  # noqa: F401  - fixture
)


def test_volume_band_rejects_a_missing_fillet():
    """Everything right except the inner fillet left off: 824 mm³ short."""
    wrong = V_EXPECTED - V_FILLET
    assert abs(wrong - V_EXPECTED) / V_EXPECTED > VOL_TOL


def test_a_wrong_hole_diameter_is_caught_by_probes_not_by_volume():
    """M6 clearance read as M6 nominal: Ø6.0 instead of Ø6.6, all four holes.

    This one found a hole in the suite. Four undersized holes remove only
    142 mm³ - 0.32 % - so the volume band is blind to it, and tightening the band
    to 0.3 % would reject legitimate kernel-level variation instead. The fix was
    to straddle the nominal radius with a pair of probes: see test_base_holes.
    """
    wrong_r = 3.0
    short = len(BASE_HOLES) * math.pi * (BASE_HOLE_R**2 - wrong_r**2) * PLATE_T
    assert short / V_EXPECTED < VOL_TOL, "volume alone would catch this; this test is stale"
    assert BASE_HOLE_R - wrong_r > PROBE_GAP, "the probes cannot resolve this error either"


def test_probes_reject_a_wrong_hole_pitch(shape):  # noqa: F811
    """Base holes at a 40 mm pitch in X instead of 48: the probe must find metal
    where the misplaced hole would be, and the correct centres must stay empty.
    """
    for x in (24.0, 64.0):
        assert material_at(shape, (x, 12.0, PLATE_T / 2)), (
            f"material expected at x = {x}; a hole there would pass the position check"
        )


def test_probes_reject_a_wrong_flange_hole_height(shape):  # noqa: F811
    """Flange holes at z = 25 instead of 28."""
    for y, _ in FLANGE_HOLES:
        assert material_at(shape, (PLATE_T / 2, y, 25.0 - 4.2 - 0.5))


def test_tolerances_are_not_vacuous():
    """A band wide enough to swallow the fillet would make test_volume theatre."""
    assert VOL_TOL * V_EXPECTED < V_FILLET
    assert VOL_TOL > 0
