"""
M-BS10 pocket test pieces ("test coupons" = 試験片)
====================================================
Wall chunks cut from the same geometry as the stepped BS10 BallCase
(cavity sphere R17.75, ball centre z=17.74, pocket azimuth 0,
elevation -26 deg), so a real M-BS10 unit can be test-fitted without
printing the whole case.

Variants (opening W x H, depth), letter engraved on the flat back:
  A: 8.8 x 7.4, depth 3.5   (tight)
  B: 9.0 x 7.6, depth 3.5   (current case value)
  C: 9.2 x 7.8, depth 3.5   (loose)
  D: 9.0 x 7.6, depth 3.2   (unit face stands 0.3 more proud)
Letters are 3x5 block glyphs, 1.5mm cells (4.5 x 7.5mm), engraved
0.8mm into the back face (x=22 plane) so they print cleanly.
Coupon block: X 13..22, Y -11..11, Z 2..17 (case-local coords).
Strip: all four on a 1.6mm base plate, order A B C D.
"""
import math, os
from build123d import *

CAV_R = 17.75
CENTRE_Z = 17.74
ELEV = -26.0
VARIANTS = [
    ("A", 8.8, 7.4, 3.5),
    ("B", 9.0, 7.6, 3.5),
    ("C", 9.2, 7.8, 3.5),
    ("D", 9.0, 7.6, 3.2),
    ("E", 9.0, 7.6, 3.35),
    ("F", 8.8, 7.6, 3.35),
    ("G", 8.6, 7.6, 3.35),
    ("H", 8.4, 7.6, 3.35),
    ("I", 8.2, 7.6, 3.35),
    ("J", 8.0, 7.6, 3.35, True),
    ("K", 8.0, 7.6, 3.35, "full"),
    ("L", 8.1, 7.6, 3.35, "full"),
    ("M", 8.2, 7.6, 3.35, "full"),
    ("N", 8.0, 7.7, 3.35, "full"),
    ("O", 8.0, 7.8, 3.35, "full"),
]
GLYPHS = {  # read from the back (+X) side: viewer right = +Y, col0 at -Y
    "A": ["010", "101", "111", "101", "101"],
    "B": ["110", "101", "110", "101", "110"],
    "C": ["011", "100", "100", "100", "011"],
    "D": ["110", "101", "101", "101", "110"],
    "E": ["111", "100", "110", "100", "111"],
    "F": ["111", "100", "110", "100", "100"],
    "G": ["011", "100", "101", "101", "011"],
    "H": ["101", "101", "111", "101", "101"],
    "I": ["111", "010", "010", "010", "111"],
    "J": ["111", "001", "001", "101", "010"],
    "K": ["101", "101", "110", "101", "101"],
    "L": ["100", "100", "100", "100", "111"],
    "M": ["101", "111", "111", "101", "101"],
    "N": ["101", "110", "101", "101", "101"],
    "O": ["010", "101", "101", "101", "010"],
}
CELL = 1.5
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ballcase34", "coupon")
os.makedirs(OUT, exist_ok=True)

el = math.radians(ELEV)
dirv = Vector(math.cos(el), 0, math.sin(el))
tang = Vector(0, 1, 0)

def engrave_letter(body, letter):
    rows = GLYPHS[letter]
    y0 = -CELL  # letter spans y -2.25..+2.25 (3 cells wide, centred 0)
    z_top = 13.25  # letter spans z 13.25 down to 5.75 (5 cells)
    for r, row in enumerate(rows):
        for cidx, bit in enumerate(row):
            if bit == "1":
                y = -1.5 * CELL + cidx * CELL
                z = z_top - (r + 1) * CELL
                body -= Solid.make_box(0.9, CELL, CELL, Plane(origin=(21.6, y, z)))
    return body

def coupon(letter, pw, ph, depth, reliefs=False):
    body = Solid.make_box(9.0, 22.0, 15.0, Plane(origin=(13.0, -11.0, 2.0)))
    body -= Solid.make_sphere(CAV_R, Plane(origin=(0, 0, CENTRE_Z)))
    # box starts 2mm inside the cavity so it truly opens through the
    # spherical surface (see case script note); floor at CAV_R + depth
    centre = dirv * (CAV_R + depth / 2 - 1.0) + Vector(0, 0, CENTRE_Z)
    pl = Plane(origin=(0, 0, 0), x_dir=tang, z_dir=dirv)
    org = centre - tang * (pw / 2) - pl.y_dir * (ph / 2) - dirv * ((depth + 2.0) / 2)
    body -= Solid.make_box(pw, ph, depth + 2.0, Plane(origin=org, x_dir=tang, z_dir=dirv))
    if reliefs:
        # side reliefs: "mouth" = case geometry (front 3.0mm only);
        # "full" = channels running the pocket's full depth
        rlen = (depth + 2.0) if reliefs == "full" else 3.0
        for sx in (-2.6, pw - 0.9):
            o = org + tang * sx + pl.y_dir * ((ph - 4.4) / 2)
            body -= Solid.make_box(3.5, 4.4, rlen, Plane(origin=o, x_dir=tang, z_dir=dirv))
    body = engrave_letter(body, letter)
    assert body.is_valid
    return body

solids = []
for i, v in enumerate(VARIANTS):
    letter, pw, ph, dep = v[0], v[1], v[2], v[3]
    c = coupon(letter, pw, ph, dep, reliefs=(v[4] if len(v) > 4 else False))
    tag = f"W{int(pw*10)}-H{int(ph*10)}-D{int(dep*10)}"
    export_stl(c, os.path.join(OUT, f"BS10-testpiece-{letter}-{tag}.stl"))
    export_step(c, os.path.join(OUT, f"BS10-testpiece-{letter}-{tag}.step"))
    solids.append(c.moved(Location(Vector(0, i * 24.0, 0))))
    print(f"{letter} {tag}: vol {c.volume:.0f}")

strip = solids[0]
for s in solids[1:]:
    strip += s
strip += Solid.make_box(11.0, 98.0, 1.6, Plane(origin=(12.0, -13.0, 0.4)))
assert strip.is_valid
bb = strip.bounding_box()
print(f"strip: vol {strip.volume:.0f}  X[{bb.min.X:.1f},{bb.max.X:.1f}] Y[{bb.min.Y:.1f},{bb.max.Y:.1f}] Z[{bb.min.Z:.1f},{bb.max.Z:.1f}]")
export_stl(strip, os.path.join(OUT, "BS10-testpiece-strip-ABCD.stl"))
export_step(strip, os.path.join(OUT, "BS10-testpiece-strip-ABCD.step"))
print("wrote to", OUT)
