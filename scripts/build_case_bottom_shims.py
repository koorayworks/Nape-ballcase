"""Bottom shims for the 34mm stepped BallCase.

Plates matching the case's bottom footprint (34.9 x 34.9, corner R12)
that sit between the BallCase and the Top-case seat, raising the whole
case (and ball) by the plate thickness. Cutouts: sensor window dia 13
at the centre, dia 7.2 clearance holes over the two magnet pockets at
(10, -10.5) / (-10, 10.5). One plate each of 0.3 / 0.5 / 0.7 mm in a
row (left to right).
"""
from build123d import *
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ballcase34")
plates = []
for i, t in enumerate((0.3, 0.5, 0.7)):
    p = extrude(RectangleRounded(34.9, 34.9, 12.0), t)
    p -= Solid.make_cylinder(6.5, t + 2.0, Plane(origin=(0, 0, -1.0)))
    for hx, hy in [(10.0, -10.5), (-10.0, 10.5)]:
        p -= Solid.make_cylinder(3.6, t + 2.0, Plane(origin=(hx, hy, -1.0)))
    plates.append(Pos(i * 38.0, 0, 0) * p)
body = plates[0]
for p in plates[1:]:
    body += p
assert body.is_valid
export_stl(body, os.path.join(OUT, "Nape-BallCase-34mm-bottom-shims.stl"))
export_step(body, os.path.join(OUT, "Nape-BallCase-34mm-bottom-shims.step"))
print("wrote bottom shims 0.3/0.5/0.7")
