"""Checks for BRACKET-SPEC, run against the exported STEP file.

The numbers below are transcribed from spec/BRACKET-SPEC.md, not imported from
solution/bracket.py. That duplication IS the check: if both sides read the same
constants, a wrong constant passes. Do not refactor it into a shared module.
"""

import math
from pathlib import Path

import cadquery as cq
import pytest
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.gp import gp_Pnt
from OCP.TopAbs import TopAbs_IN, TopAbs_ON

STEP = Path(__file__).resolve().parent.parent / "out" / "bracket.step"

# --- spec constants, transcribed from BRACKET-SPEC.md -------------------------
BASE_L, BASE_W, PLATE_T = 80.0, 60.0, 6.0
FLANGE_H = 50.0
FILLET_R = 8.0
BASE_HOLE_R = 6.6 / 2
BASE_HOLES = [(x, y) for x in (20.0, 68.0) for y in (12.0, 48.0)]
FLANGE_HOLE_R = 8.4 / 2
FLANGE_HOLES = [(y, 28.0) for y in (15.0, 45.0)]
MIN_WALL = 8.0
DENSITY = 2.70e-3  # g/mm³

V_FILLET = FILLET_R**2 * (1 - math.pi / 4) * BASE_W
V_EXPECTED = (
    BASE_L * BASE_W * PLATE_T
    + PLATE_T * BASE_W * FLANGE_H
    - PLATE_T * BASE_W * PLATE_T
    + V_FILLET
    - len(BASE_HOLES) * math.pi * BASE_HOLE_R**2 * PLATE_T
    - len(FLANGE_HOLES) * math.pi * FLANGE_HOLE_R**2 * PLATE_T
)
VOL_TOL = 0.005
LIN_TOL = 0.05  # mm
PROBE_GAP = 0.2  # mm, how far either side of a nominal radius the probes sit


@pytest.fixture(scope="module")
def shape():
    if not STEP.exists():
        pytest.fail(f"{STEP} was not produced")
    return cq.importers.importStep(str(STEP)).val()


def material_at(shape, point):
    """True if the solid has material at point, False if the point is in air."""
    classifier = BRepClass3d_SolidClassifier(shape.wrapped)
    classifier.Perform(gp_Pnt(*point), 1e-6)
    return classifier.State() in (TopAbs_IN, TopAbs_ON)


# --- R1 -----------------------------------------------------------------------
def test_bounding_box(shape):
    bb = shape.BoundingBox()
    assert bb.xlen == pytest.approx(BASE_L, abs=LIN_TOL)
    assert bb.ylen == pytest.approx(BASE_W, abs=LIN_TOL)
    assert bb.zlen == pytest.approx(FLANGE_H, abs=LIN_TOL)
    assert (bb.xmin, bb.ymin, bb.zmin) == pytest.approx((0, 0, 0), abs=LIN_TOL)


# --- R2, R3 -------------------------------------------------------------------
def test_volume(shape):
    assert shape.Volume() == pytest.approx(V_EXPECTED, rel=VOL_TOL)


def test_mass(shape):
    # Volume again, in the units the spec states the requirement in.
    assert shape.Volume() * DENSITY == pytest.approx(118.7, rel=VOL_TOL)


# --- R5 -----------------------------------------------------------------------
def test_base_holes(shape):
    """Straddles the nominal radius. Resolution is +/- PROBE_GAP on the radius,
    so a diameter error above 2 * PROBE_GAP is caught. The volume check cannot do
    this: four holes at Ø6.0 instead of Ø6.6 is 0.32 % of the solid.
    """
    for x, y in BASE_HOLES:
        z = PLATE_T / 2
        assert not material_at(shape, (x, y, z)), f"no hole at base ({x}, {y})"
        assert not material_at(shape, (x + BASE_HOLE_R - PROBE_GAP, y, z)), f"base hole ({x}, {y}) is undersized"
        assert material_at(shape, (x + BASE_HOLE_R + PROBE_GAP, y, z)), f"base hole ({x}, {y}) is oversized"


def test_flange_holes(shape):
    for y, z in FLANGE_HOLES:
        x = PLATE_T / 2
        assert not material_at(shape, (x, y, z)), f"no hole in flange at ({y}, {z})"
        assert not material_at(shape, (x, y, z + FLANGE_HOLE_R - PROBE_GAP)), f"flange hole ({y}, {z}) is undersized"
        assert material_at(shape, (x, y, z + FLANGE_HOLE_R + PROBE_GAP)), f"flange hole ({y}, {z}) is oversized"


# --- R6 -----------------------------------------------------------------------
def test_inner_fillet(shape):
    """The fillet arc is centred at (FILLET_R + PLATE_T, *, FILLET_R + PLATE_T).

    Inside that arc is air, outside it - but still in the corner - is material.
    """
    c = FILLET_R + PLATE_T  # 14.0
    y = BASE_W / 2
    assert material_at(shape, (PLATE_T + 2, y, PLATE_T + 2)), "corner is empty: fillet missing"
    assert not material_at(shape, (c - 2, y, c - 2)), "corner is square: fillet missing"


# --- R4 -----------------------------------------------------------------------
def test_minimum_wall(shape):
    """ponytail: probes the four thinnest webs the spec creates, not a general
    thickness solver. A general one needs a medial-axis pass; add it only if a
    future revision puts a hole somewhere this list does not cover.
    """
    webs = [
        (20.0, BASE_HOLE_R + MIN_WALL / 2, PLATE_T / 2),           # hole (20, 12) -> face y = 0
        (20.0, BASE_W - BASE_HOLE_R - MIN_WALL / 2, PLATE_T / 2),   # hole (20, 48) -> face y = 60
        (BASE_L - BASE_HOLE_R - MIN_WALL / 2, 12.0, PLATE_T / 2),   # hole (68, 12) -> face x = 80
        (PLATE_T / 2, FLANGE_HOLE_R + MIN_WALL / 2, 28.0),          # flange hole (15, 28) -> face y = 0
    ]
    for p in webs:
        assert material_at(shape, p), f"web at {p} is missing - wall below {MIN_WALL} mm"

    # And the webs really are at least MIN_WALL wide per the spec geometry.
    for x, y in BASE_HOLES:
        edges = [x - BASE_HOLE_R, BASE_L - x - BASE_HOLE_R, y - BASE_HOLE_R, BASE_W - y - BASE_HOLE_R]
        assert min(edges) >= MIN_WALL, f"base hole ({x}, {y}) sits {min(edges):.1f} mm from an edge"
    for y, z in FLANGE_HOLES:
        edges = [y - FLANGE_HOLE_R, BASE_W - y - FLANGE_HOLE_R, FLANGE_H - z - FLANGE_HOLE_R]
        assert min(edges) >= MIN_WALL, f"flange hole ({y}, {z}) sits {min(edges):.1f} mm from an edge"
