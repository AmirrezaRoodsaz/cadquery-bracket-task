# BRACKET-SPEC — L-bracket, test-rig sensor mount

All dimensions in millimetres. Material: aluminium 6061, density 2.70 g/cm³.

Coordinate system: right-handed, origin at the outer corner of the base plate.
The base plate lies in +X/+Y, material from z = 0 upward.

## Geometry

**Base plate**
- 80.0 long (X) × 60.0 wide (Y) × 6.0 thick (Z)
- Occupies x ∈ [0, 80], y ∈ [0, 60], z ∈ [0, 6]

**Vertical flange**
- Rises from the x = 0 edge of the base plate
- 6.0 thick (X) × 60.0 wide (Y) × 50.0 tall (Z)
- Occupies x ∈ [0, 6], y ∈ [0, 60], z ∈ [0, 50]

**Inner fillet**
- Radius 8.0 on the single concave edge between the top face of the base plate
  (z = 6) and the inner face of the flange (x = 6)
- Runs the full width, y = 0 to y = 60

**Base mounting holes** — 4 off, through the base plate in Z
- Ø 6.6 (clearance for M6)
- Centres at x = 20.0 and x = 68.0, y = 12.0 and y = 48.0

**Flange mounting holes** — 2 off, through the flange in X
- Ø 8.4 (clearance for M8)
- Centres at y = 15.0 and y = 45.0, z = 28.0

## Requirements the part must satisfy

| # | Requirement | Value |
|---|---|---|
| R1 | Overall bounding box | 80.0 × 60.0 × 50.0, lower corner at the origin |
| R2 | Volume | 43 978 mm³ ± 0.5 % |
| R3 | Mass | 118.7 g ± 0.5 % |
| R4 | Minimum wall between any hole edge and the nearest outer face | ≥ 8.0 |
| R5 | All six holes through, at the stated centres | — |
| R6 | Inner fillet present at the stated radius | — |

R2 is the sum of base, flange and fillet material minus the six holes:

```
28 800  base            80 × 60 × 6
+18 000 flange           6 × 60 × 50
- 2 160 shared corner    6 × 60 × 6
+   824 fillet           8² · (1 − π/4) · 60
-   821 4 base holes     4 · π · 3.3² · 6
-   665 2 flange holes   2 · π · 4.2² · 6
-------
 43 978 mm³  →  43.978 cm³ × 2.70 g/cm³ = 118.7 g
```

## Deliverable

`out/bracket.step` — the solid, exported as AP214 STEP.

The checks read that STEP file. They do not read the script that produced it.
