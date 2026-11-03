"""
Nape BallCase 34mm STEPPED - ELECOM support-unit version
================================================================
Same stepped 34mm BallCase as build_ballcase_34_stepped.py, but the
ball supports are receiver pockets for ELECOM replacement support
units instead of loose 6mm balls. The unit fitted is the M-TU03SS
ball-roller unit (dia 2.5 support ball on 4 auxiliary balls); its
socket (8 x 7 x 4 mm) is common with the M-BS10 / M-RS10, so the
pocket dimensions carry over. (Filename keeps the legacy "BS10".)

Reference: usm916/HUGE_BU_MOD (tray that puts M-BS10 units into an
Elecom HUGE, replacing its ruby supports). In the HUGE tray the
units sit in notches in the cup wall, roller facing the ball.
Cross-checked against the HUGE tray STL (measured 2026-10-29):
pocket floor 30.0-30.5 from the ball centre (depth 3.3-3.8 beyond
the cavity surface), pockets ~120 deg apart, elevation -20..-30.

FINAL pocket spec (decided by printed test pieces, see
build_bs10_coupon.py; print-confirmed 2026-11-01):
  opening 8.0 (tangential) x 7.7 (along wall), depth 3.35 from the
  cavity tangent plane (floor at centre distance 21.10), full-depth
  side relief channels 3.5 x 4.4, azimuths 0/120/240, elevation
  -26 deg. Ball mouth opening dia 33.95 (rim height sets it; dia
  34.10 let the ball fall out when inverted, dia 33.90 was tight).
  Still unverified: TU03SS contact protrusion / support height with
  a real unit in this case.

Outer shape, neck, sensor window and bottom pockets are identical
to build_ballcase_34_stepped.py. See that file for the interface
notes. Ball centre z=17.74, cavity R17.75, top z=23.54.
"""
import math, os
from build123d import *

BALL_R = 17.0
CAV_R = 17.75
CENTRE_Z = 17.74
TOP_Z = CENTRE_Z + 5.19   # rim height sets the mouth opening on the sphere: at +5.19 the opening is dia 33.95 (see mouth note). Overall height 22.93 (was 23.54; a +4.8 rim gave dia 34.18 and the ball fell out when inverted - user print feedback 2026-11-01)
SENSOR_R = 6.5

# Support-unit pocket parameters - FINAL, decided by test-piece prints
# (2026-10-31, user's hand BS10 used for socket check; socket is common
# with the M-TU03SS the user will actually fit):
#   width 8.0 + full-depth side reliefs = test piece K (good fit)
#   height: 7.6 slightly tight in the case, 7.8 too loose -> 7.7
#   depth 3.35 (3.5 tight, 3.2 a bit loose in the test pieces)
PK_W = 8.0        # tangential (test piece J/K, user: feels good 2026-11-01)
PK_H = 7.7        # along wall (unit D7 + 0.7) - final: 7.6 slightly tight in the case, 7.8 (variant O) too loose, 7.7 (variant N) adopted 2026-11-01
PK_DEPTH = 3.35   # from cavity-sphere tangent plane outward
PK_AZ = [0.0, 120.0, 240.0]
PK_ELEV = -26.0   # deg; measured from the HUGE tray STL: pockets sit at el -20..-30 (centre ~-25)

PROFILES = [
    (0.0,   34.9, 12.0),
    (3.0,   34.9, 12.0),
    (6.5,   44.0, 14.0),
    (13.0,  44.0, 14.0),
    (17.5,  43.0, 16.0),
    (20.5,  41.0, 18.0),
    (TOP_Z, 39.0, 18.5),
]
sections = [Plane.XY.offset(z) * RectangleRounded(w, w, r) for z, w, r in PROFILES]
body = loft(sections, ruled=True)
body -= Solid.make_sphere(CAV_R, Plane(origin=(0, 0, CENTRE_Z)))
# mouth trim (2026-11-01, user print feedback: ball tight in/out):
# the sphere alone leaves a rim opening of only dia 33.55 for the 34mm
# ball (0.45 snap interference, worse with print shrinkage). A short
# cylinder from centre+4 widens the mouth. History (user prints):
# r16.95 (dia 33.90) still a bit tight; r17.05 (dia 34.10) let the
# ball fall out when inverted. The rim height now sets the opening
# (dia 33.95 on the sphere at TOP_Z); this trim at r16.90 stays below
# the sphere at the rim and is only a safeguard. Seating unaffected.
body -= Solid.make_cylinder(16.90, 6.0, Plane(origin=(0, 0, CENTRE_Z + 4.0)))
body -= Solid.make_cylinder(SENSOR_R, 8.0, Plane(origin=(0, 0, -1.0)))

el = math.radians(PK_ELEV)
for azd in PK_AZ:
    az = math.radians(azd)
    dirv = Vector(math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el))
    tang = Vector(-math.sin(az), math.cos(az), 0)
    # NOTE: box must start INSIDE the cavity (CAV_R - 2). A flat box
    # starting exactly at the tangent plane never breaks the spherical
    # surface (sphere curves away from the plane) and leaves the pocket
    # sealed inside the wall behind a ~0.5mm membrane. Floor stays at
    # CAV_R + PK_DEPTH.
    centre = dirv * (CAV_R + PK_DEPTH / 2 - 1.0) + Vector(0, 0, CENTRE_Z)
    # build box in a plane whose z axis is dirv and x axis is tang
    pl = Plane(origin=(0, 0, 0), x_dir=tang, z_dir=dirv)
    y_dir = pl.y_dir
    org = centre - tang * (PK_W / 2) - y_dir * (PK_H / 2) - dirv * ((PK_DEPTH + 2.0) / 2)
    pl = Plane(origin=org, x_dir=tang, z_dir=dirv)
    body -= Solid.make_box(PK_W, PK_H, PK_DEPTH + 2.0, pl)
    # side reliefs (user request 2026-10-31, replacing an earlier
    # top+bottom version): slots opening the pocket's left and right
    # rims at the mouth, like the flex space beside the clips in the
    # genuine Elecom socket, so a tool or nail can grip the unit's
    # side edges. They cover only the unit's front ~1.65mm; the rear
    # of the pocket keeps the full tested 8.2 grip.
    for sx in (-2.6, PK_W - 0.9):
        notch_org_s = org + tang * sx + y_dir * ((PK_H - 4.4) / 2)
        pl_s = Plane(origin=notch_org_s, x_dir=tang, z_dir=dirv)
        body -= Solid.make_box(3.5, 4.4, PK_DEPTH + 2.0, pl_s)  # full-depth channels (test piece K)

# diagonal bottom pockets (original interface, as in the base model)
for (px, py) in [(10.0, -10.5), (-10.0, 10.5)]:
    # genuine shape (measured from the original STL, 2026-11-01):
    # regular hexagon, circumradius 3.4 - across flats 5.89 (X),
    # across corners 6.80 (Y, vertices on +/-Y), depth ~3.1.
    # The earlier "5.9 x 6.8 rectangle" was just its bounding box.
    hex_pts = [(3.4 * math.cos(math.radians(90 + 60 * k)),
                3.4 * math.sin(math.radians(90 + 60 * k))) for k in range(6)]
    hex_face = Polygon(*[Vector(px + hx, py + hy, -0.5) for hx, hy in hex_pts])
    body -= extrude(hex_face, amount=3.6)

assert body.is_valid, "not a valid solid"
bb = body.bounding_box()
print(f"valid solid, volume={body.volume:.0f} mm^3")
print(f"bbox X[{bb.min.X:.2f},{bb.max.X:.2f}] Y[{bb.min.Y:.2f},{bb.max.Y:.2f}] Z[{bb.min.Z:.2f},{bb.max.Z:.2f}]")

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ballcase34")
os.makedirs(OUT, exist_ok=True)
export_stl(body, os.path.join(OUT, "Nape-BallCase-34mm-stepped-BS10.stl"))
export_step(body, os.path.join(OUT, "Nape-BallCase-34mm-stepped-BS10.step"))
print("wrote STL + STEP to", OUT)
