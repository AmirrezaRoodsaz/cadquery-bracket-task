# cadquery-bracket-task

A parametric mechanical part written as code, exported to STEP, and verified by
a test suite that reads the STEP back and measures it.

```
./run.sh
```

Builds the image, generates the part, runs the checks. Exit code 0 means the
solid meets every requirement in [`spec/BRACKET-SPEC.md`](spec/BRACKET-SPEC.md).
Nothing is installed on the host.

## What is here

| | |
|---|---|
| `spec/BRACKET-SPEC.md` | The requirement. Dimensions, tolerances, and the arithmetic behind the expected volume. |
| `solution/bracket.py` | Reference solution. ~60 lines of CadQuery; writes `out/bracket.step`. |
| `tests/test_bracket.py` | The checks: bounding box, volume, mass, hole positions, fillet, minimum wall. |
| `tests/test_checks_catch_mistakes.py` | Checks on the checks. See below. |
| `Dockerfile` | Reproduces the whole thing from a clean `python:3.11-slim`. |

## The part

An L-bracket: 80 × 60 × 6 base plate, 50 mm flange, 8 mm inner fillet, four M6
clearance holes through the base and two M8 clearance holes through the flange.
Aluminium 6061. 43 978 mm³, 118.7 g.

## How verification works here

The tests do not import `solution/bracket.py`. They load `out/bracket.step` and
measure the solid, so a script that reports success without producing correct
geometry fails. Two kinds of check:

**Measured against an independent prediction.** Volume is not compared to
"whatever the reference produced". It is compared to a figure derived
analytically from the spec constants — base plus flange minus shared corner plus
fillet minus six cylinders. The spec numbers are transcribed into the test file
by hand rather than imported, because a shared constants module would let a
wrong number agree with itself.

**Point classification.** Hole positions, the fillet, and wall thickness are
checked by asking the geometry kernel whether a given point is inside the solid
(`BRepClass3d_SolidClassifier`). A hole centre must be air; a point just outside
its nominal radius must be metal. That catches a hole that is missing, displaced,
or oversized, in one assertion each.

## Why the second test file exists

A suite that has only ever been run against the right answer proves nothing about
its own discrimination. `tests/test_checks_catch_mistakes.py` pins down which
check catches which mistake, and it earned its place on the first run: it failed,
correctly.

The claim it disproved was mine. I had assumed the volume band would catch a
wrong hole diameter. It does not — four holes at Ø6.0 instead of Ø6.6 remove
142 mm³, which is 0.32 % of the solid and sits inside the 0.5 % band. Tightening
the band to 0.3 % would have been the wrong fix: it would start rejecting
legitimate kernel-level variation. The right fix was to straddle each nominal
radius with a pair of probes — air just inside it, metal just outside — which
resolves a radius error of more than 0.2 mm regardless of how little volume it
moves. `test_base_holes` now does that, and the meta-test asserts the volume band
*cannot* catch this, so the two checks cannot silently swap responsibilities.

Verified against deliberately broken parts, by patching one constant in the
reference solution and rebuilding:

| Injected mistake | Caught by |
|---|---|
| Inner fillet dropped to R0.1 | `test_volume`, `test_mass`, `test_inner_fillet` |
| Base holes Ø6.0 instead of Ø6.6 | `test_base_holes` — and *not* by volume, as predicted |
| Base hole pitch 40 instead of 48 | `test_base_holes`, `test_probes_reject_a_wrong_hole_pitch` |

If someone later widens a tolerance to make a failing build pass, the meta-tests
fail first.

## Known ceiling

`test_minimum_wall` probes the four thinnest webs this specific geometry creates.
It is not a general minimum-thickness solver — that needs a medial-axis pass. The
limitation is marked in the test. Add the general version only when a revision
puts a hole somewhere the probe list does not cover.

## Swapping in your own solution

Replace `solution/bracket.py` with anything that writes `out/bracket.step`, in
any language. The checks do not care how the file was made.

## Using it as a benchmark task

Delete `solution/bracket.py`, hand an agent the container and this instruction:

> Read `spec/BRACKET-SPEC.md`. Write `solution/bracket.py` so that running it
> produces `out/bracket.step` meeting every requirement. Then `pytest -q tests/`
> must pass.

The spec is closed — every dimension and tolerance needed is in it, and nothing
in it is ambiguous. The reference solution takes about 25 minutes to write from
scratch if you know CadQuery and about an hour if you are learning it, which is
the 60–75 minute band these benchmarks aim for.
