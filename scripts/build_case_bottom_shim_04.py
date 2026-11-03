"""Single-thickness (0.4 mm) bottom shim for the 34mm stepped BallCase.
Same footprint/cutouts as build_case_bottom_shims.py; 3 copies in a row."""
from build123d import *
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ballcase34")
plates = []
for i in range(3):
    p = extrude(RectangleRounded(34.9, 34.9, 12.0), 0.4)
    p -= Solid.make_cylinder(6.5, 2.4, Plane(origin=(0, 0, -1.0)))
    for hx, hy in [(10.0, -10.5), (-10.0, 10.5)]:
        p -= Solid.make_cylinder(3.6, 2.4, Plane(origin=(hx, hy, -1.0)))
    plates.append(Pos(i * 38.0, 0, 0) * p)
body = plates[0]
for p in plates[1:]:
    body += p
assert body.is_valid
export_stl(body, os.path.join(OUT, "Nape-BallCase-34mm-bottom-shim-04.stl"))
export_step(body, os.path.join(OUT, "Nape-BallCase-34mm-bottom-shim-04.step"))
print("wrote 0.4mm bottom shims x3")
