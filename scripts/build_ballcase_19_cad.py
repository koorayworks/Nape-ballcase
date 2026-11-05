"""Nape BallCase 19mm - CAD rebuild (build123d) with ELECOM support-unit pockets.

Replicates the genuine case (measured from the official STL on 2026-11-05)
but with a true analytic cavity sphere instead of the faceted mesh:
  - body: rounded square 35x35, corner R12 at the base, with a smooth
    dome top (lofted through measured width/corner-R samples) up to
    the top at z=14.40
  - outline centre offset from ball axis: (+0.09, 0.00)
  - cavity: sphere R10.25, centre (0, 0, 10.15); rim opening dia ~18.65
    (from sphere x top plane, same as genuine)
  - sensor window: dia 13 cylinder on the ball axis, through the bottom
  - bottom magnet pockets: regular hexagons, circumradius 3.4 (across
    flats 5.89 in X, across corners 6.80 in Y, vertices on +/-Y),
    depth 3.1, centres (+10.6, -10.4) / (-10.6, +10.4) rel. outline centre
  - unit pockets (same spec family as the 25/34mm cases): opening
    8.0 x PK_H, depth 3.35 (floor at centre distance 13.60), full-depth
    side relief channels 3.5 x 4.4, azimuths 0/120/240, elevation -26 deg.
    Pocket height defaults to 7.5: the tighter cavity curvature opens
    the mouth more (34mm R17.75 -> 7.7 print-confirmed, 25mm R13.25 ->
    7.6 print-confirmed, so 19mm R10.25 extrapolates to ~7.5).
    Pockets replace the genuine support dimples entirely.
Local frame: origin on the ball axis at the bottom face, ball centre z=10.15.
"""

import math
import os

from build123d import *

BALL_R = 9.5
CAV_R = 10.25
CENTRE_Z = 10.15
TOP_Z = 14.40
OUTLINE_C = (0.09, 0.00)  # case outline centre rel. ball axis

PK_W = 8.0        # pocket opening, tangential (final spec, 2026-11-01)
PK_H = float(os.environ.get("NAPE_PK_H", "7.5"))  # pocket opening, along the wall
PK_TAG = os.environ.get("NAPE_PK_TAG", "")
PK_DEPTH = 3.35   # from the cavity tangent plane; floor at CAV_R + 3.35
PK_AZ = [0.0, 120.0, 240.0]
PK_ELEV = -26.0

# --- body: lofted rounded-square prism with measured dome profile ---
# (z, width, corner R) sampled from the genuine STL sections 2026-11-05;
# the last profile is a short extrapolation so the rim circle (r 9.33
# around the ball axis) stays inside the top face.
profiles = [
    (0.0, 35.00, 12.05),
    (2.0, 35.00, 12.06),
    (3.0, 34.93, 12.08),
    (4.0, 34.79, 12.12),
    (5.0, 34.41, 11.77),
    (6.0, 33.93, 11.66),
    (7.0, 33.20, 11.13),
    (8.0, 32.27, 10.73),
    (9.0, 31.15, 10.25),
    (10.0, 29.70, 9.53),
    (11.0, 27.87, 8.47),
    (12.0, 25.57, 7.45),
    (12.5, 24.25, 6.83),
    (13.0, 22.54, 5.92),
    (13.5, 20.51, 5.01),
    (TOP_Z, 19.20, 4.40),
]
sections = [Plane.XY.offset(z) * RectangleRounded(w, w, r) for z, w, r in profiles]
body = loft(sections, ruled=True)
body = Pos(OUTLINE_C[0], OUTLINE_C[1], 0) * body

# --- ball cavity: exact sphere ---
body -= Solid.make_sphere(CAV_R, Plane(origin=(0, 0, CENTRE_Z)))

# --- sensor window: dia 13 through the bottom on the ball axis ---
body -= Solid.make_cylinder(6.5, 8.0, Plane(origin=(0.0, 0.0, -1.0)))

# --- bottom magnet pockets: hexagons, depth 3.1 (cutter from z=-0.5) ---
for hx, hy in [(10.6, -10.4), (-10.6, 10.4)]:
    px, py = OUTLINE_C[0] + hx, OUTLINE_C[1] + hy
    hex_pts = [
        (3.4 * math.cos(math.radians(90 + 60 * k)),
         3.4 * math.sin(math.radians(90 + 60 * k)))
        for k in range(6)
    ]
    hex_face = Polygon(*[Vector(px + x, py + y, -0.5) for x, y in hex_pts])
    body -= extrude(hex_face, amount=3.6)

# --- support-unit pockets (same construction as the 25/34mm cases) ---
el = math.radians(PK_ELEV)
for azd in PK_AZ:
    az = math.radians(azd)
    dirv = Vector(math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el))
    tang = Vector(-math.sin(az), math.cos(az), 0)
    # box starts INSIDE the cavity (CAV_R - 2) so it actually breaks the
    # spherical surface; floor stays at CAV_R + PK_DEPTH = 13.60
    centre = dirv * (CAV_R + PK_DEPTH / 2 - 1.0) + Vector(0, 0, CENTRE_Z)
    pl = Plane(origin=(0, 0, 0), x_dir=tang, z_dir=dirv)
    y_dir = pl.y_dir
    org = centre - tang * (PK_W / 2) - y_dir * (PK_H / 2) - dirv * ((PK_DEPTH + 2.0) / 2)
    pl = Plane(origin=org, x_dir=tang, z_dir=dirv)
    body -= Solid.make_box(PK_W, PK_H, PK_DEPTH + 2.0, pl)
    # full-depth side relief channels (test piece K spec)
    for sx in (-2.6, PK_W - 0.9):
        notch_org = org + tang * sx + y_dir * ((PK_H - 4.4) / 2)
        pl_s = Plane(origin=notch_org, x_dir=tang, z_dir=dirv)
        body -= Solid.make_box(3.5, 4.4, PK_DEPTH + 2.0, pl_s)

assert body.is_valid, "not a valid solid"
bb = body.bounding_box()
print(f"valid solid, volume={body.volume:.0f} mm^3")
print(f"bbox X[{bb.min.X:.2f},{bb.max.X:.2f}] Y[{bb.min.Y:.2f},{bb.max.Y:.2f}] Z[{bb.min.Z:.2f},{bb.max.Z:.2f}]")

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ballcase19")
os.makedirs(OUT, exist_ok=True)
export_stl(body, os.path.join(OUT, f"Nape-BallCase-19mm-unitpockets-CAD{PK_TAG}.stl"))
export_step(body, os.path.join(OUT, f"Nape-BallCase-19mm-unitpockets-CAD{PK_TAG}.step"))
print("wrote STL + STEP to", OUT)
