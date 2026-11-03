"""Nape BallCase 25mm - CAD rebuild (build123d) with ELECOM support-unit pockets.

Replicates the genuine case (measured from the official STL on 2026-11-01)
but with a true analytic cavity sphere instead of the faceted mesh:
  - body: rounded square 35x35, corner R12, straight walls to z~10,
    then a top perimeter ball fillet R8 up to the top at z=17.99
    (lofted through samples of the fillet arc)
  - outline centre offset from ball axis: (+0.09, +0.25)
  - cavity: sphere R13.25, centre (0, 0, 13.24); rim opening ~dia 24.8
  - sensor window: dia 13 cylinder at (+0.42, +0.09), through the bottom
  - bottom magnet pockets: regular hexagons, circumradius 3.4 (across
    flats 5.89 in X, across corners 6.80 in Y, vertices on +/-Y),
    depth 3.1, centres (-10.5, +10.5) / (+10.5, -10.5) rel. outline centre
  - unit pockets (same spec as the 34mm case): opening 8.0 x 7.7,
    depth 3.35 (floor at centre distance 16.60), full-depth side relief
    channels 3.5 x 4.4, azimuths 0/120/240, elevation -26 deg.
    Pockets replace the genuine support dimples entirely.
Local frame: origin on the ball axis at the bottom face, ball centre z=13.24.
"""

import math
import os

from build123d import *

BALL_R = 12.5
CAV_R = 13.25
CENTRE_Z = 13.24
TOP_Z = 17.99
OUTLINE_C = (0.09, 0.25)  # case outline centre rel. ball axis

PK_W = 8.0        # pocket opening, tangential (final spec, 2026-11-01)
PK_H = float(os.environ.get("NAPE_PK_H", "7.6"))  # pocket opening, along the wall (7.7 was loose up/down in the 25mm case - tighter wall curvature opens the mouth more; 7.6 print-confirmed just right 2026-11-03. The 34mm case uses 7.7.)
PK_TAG = os.environ.get("NAPE_PK_TAG", "")
PK_DEPTH = 3.35   # from the cavity tangent plane; floor at CAV_R + 3.35
PK_AZ = [0.0, 120.0, 240.0]
PK_ELEV = -26.0

# --- body: lofted rounded-square prism with R8 top fillet profile ---
FILLET_R = 8.0
FILLET_Z0 = TOP_Z - FILLET_R  # fillet starts at z = 9.99
profiles = [(0.0, 35.0, 12.0), (FILLET_Z0, 35.0, 12.0)]
for z in (11.0, 12.5, 14.0, 15.25, 16.25, 17.0, 17.6, 17.9, TOP_Z):
    dz = z - FILLET_Z0
    inset = FILLET_R - math.sqrt(FILLET_R**2 - dz**2)
    profiles.append((z, 35.0 - 2 * inset, 12.0 - inset))
sections = [Plane.XY.offset(z) * RectangleRounded(w, w, r) for z, w, r in profiles]
body = loft(sections, ruled=True)
body = Pos(OUTLINE_C[0], OUTLINE_C[1], 0) * body

# --- ball cavity: exact sphere ---
body -= Solid.make_sphere(CAV_R, Plane(origin=(0, 0, CENTRE_Z)))

# --- sensor window: dia 13 through the bottom at (+0.42, +0.09) ---
body -= Solid.make_cylinder(6.5, 8.0, Plane(origin=(0.42, 0.09, -1.0)))

# --- bottom magnet pockets: hexagons, depth 3.1 (cutter from z=-0.5) ---
for hx, hy in [(-10.5, 10.5), (10.5, -10.5)]:
    px, py = OUTLINE_C[0] + hx, OUTLINE_C[1] + hy
    hex_pts = [
        (3.4 * math.cos(math.radians(90 + 60 * k)),
         3.4 * math.sin(math.radians(90 + 60 * k)))
        for k in range(6)
    ]
    hex_face = Polygon(*[Vector(px + x, py + y, -0.5) for x, y in hex_pts])
    body -= extrude(hex_face, amount=3.6)

# --- support-unit pockets (same construction as the 34mm case) ---
el = math.radians(PK_ELEV)
for azd in PK_AZ:
    az = math.radians(azd)
    dirv = Vector(math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el))
    tang = Vector(-math.sin(az), math.cos(az), 0)
    # box starts INSIDE the cavity (CAV_R - 2) so it actually breaks the
    # spherical surface; floor stays at CAV_R + PK_DEPTH = 16.60
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

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ballcase25")
os.makedirs(OUT, exist_ok=True)
export_stl(body, os.path.join(OUT, f"Nape-BallCase-25mm-unitpockets-CAD{PK_TAG}.stl"))
export_step(body, os.path.join(OUT, f"Nape-BallCase-25mm-unitpockets-CAD{PK_TAG}.step"))
print("wrote STL + STEP to", OUT)
