"""Reference solution for BRACKET-SPEC: parametric L-bracket in CadQuery.

Writes out/bracket.step. Nothing here is read by the tests - they load the
exported STEP and measure it. Change any number below and the tests fail.
"""

from pathlib import Path

import cadquery as cq

BASE_L = 80.0
BASE_W = 60.0
PLATE_T = 6.0
FLANGE_H = 50.0
FILLET_R = 8.0

BASE_HOLE_D = 6.6
BASE_HOLE_X = (20.0, 68.0)
BASE_HOLE_Y = (12.0, 48.0)

FLANGE_HOLE_D = 8.4
FLANGE_HOLE_Y = (15.0, 45.0)
FLANGE_HOLE_Z = 28.0

OUT = Path(__file__).resolve().parent.parent / "out" / "bracket.step"


def build():
    base = cq.Workplane("XY").box(BASE_L, BASE_W, PLATE_T, centered=False)
    flange = cq.Workplane("XY").box(PLATE_T, BASE_W, FLANGE_H, centered=False)
    part = base.union(flange)

    # The one concave edge, at x = z = PLATE_T running along Y.
    inner_edge = cq.selectors.NearestToPointSelector((PLATE_T, BASE_W / 2, PLATE_T))
    part = part.edges(inner_edge).fillet(FILLET_R)

    # Cutters are 1 mm proud at both ends so the holes are unambiguously through.
    for x in BASE_HOLE_X:
        for y in BASE_HOLE_Y:
            cutter = (
                cq.Workplane("XY")
                .center(x, y)
                .circle(BASE_HOLE_D / 2)
                .extrude(PLATE_T + 2)
                .translate((0, 0, -1))
            )
            part = part.cut(cutter)

    for y in FLANGE_HOLE_Y:
        cutter = (
            cq.Workplane("YZ")
            .center(y, FLANGE_HOLE_Z)
            .circle(FLANGE_HOLE_D / 2)
            .extrude(PLATE_T + 2)
            .translate((-1, 0, 0))
        )
        part = part.cut(cutter)

    return part


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(build(), str(OUT))
    print(f"wrote {OUT}")
