"""
Nape BallCase 34mm - STEPPED version (prototype)
=================================================
Keeps the original 25mm BallCase fit interface to the Top case
unchanged, and widens to 44mm only ABOVE the Top case top surface.

Local coords: ball-centre axis at (0,0), bottom face at z=0.
Assembled coords (official case): add (-0.5, -0.25, 13.0).

Interface kept from the original (measured from official STLs):
  - bottom face flat at z=0 (sits on the Top case deck at Z=13)
  - neck footprint 35 x 35, corner R11, up to z=3 (global 16,
    i.e. 1mm above the Top top surface at global 15)
  - sensor window dia.13 through the bottom, on the ball axis
  - two diagonal bottom pockets: regular hexagon (across flats 5.89 / corners 6.80), depth 3.1,
    centres (+10,-10.5) and (-10,+10.5)  (as in the original)

34mm ball geometry (clearances carried over from the original):
  - ball R17, cavity R17.75 (0.75 clearance, same as original)
  - ball bottom 0.74 above the bottom face (same as original)
    -> ball centre z = 17.74
  - rim plane at centre +5.8 -> top z = 23.54, opening R16.78
    (0.22 lip over the ball, original was 0.09)

Bearings: Deck-series arrangement (NOT the original dimples):
  3x dia.6 bearing balls, pocket R3.3, centre distance 20 from
  ball centre, azimuth 30/150/270, tilt 55deg from downward vertical.

Outer profile (loft, rounded squares):
  z=0     35 x 35  R11   (neck)
  z=3     35 x 35  R11
  z=6.5   44 x 44  R14   (flare)
  z=13    44 x 44  R14
  z=17.5  43 x 43  R16
  z=20.5  41 x 41  R18
  z=23.54 39 x 39  R18.5 (top, near-circular)
"""
import math, os
from build123d import *

BALL_R = 17.0
CAV_R = 17.75
CENTRE_Z = 17.74
TOP_Z = CENTRE_Z + 5.8          # 23.54
SENSOR_R = 6.5
BEARING_R = 3.0
POCKET_R = BEARING_R + 0.3
BEARING_DIST = BALL_R + BEARING_R   # 20
BEARING_AZ = [30.0, 150.0, 270.0]
BEARING_TILT = 55.0             # deg from downward vertical

PROFILES = [  # (z, width, corner_r)
    (0.0,   35.0, 11.0),
    (3.0,   35.0, 11.0),
    (6.5,   44.0, 14.0),
    (13.0,  44.0, 14.0),
    (17.5,  43.0, 16.0),
    (20.5,  41.0, 18.0),
    (TOP_Z, 39.0, 18.5),
]

sections = []
for z, w, r in PROFILES:
    f = Plane.XY.offset(z) * RectangleRounded(w, w, r)
    sections.append(f)
body = loft(sections, ruled=True)

# ball cavity
body -= Solid.make_sphere(CAV_R, Plane(origin=(0, 0, CENTRE_Z)))
# sensor window (straight dia.13 like the original)
body -= Solid.make_cylinder(SENSOR_R, 8.0, Plane(origin=(0, 0, -1.0)))
# bearing pockets
tilt = math.radians(BEARING_TILT)
for azd in BEARING_AZ:
    az = math.radians(azd)
    hr = BEARING_DIST * math.sin(tilt)
    cx, cy = hr * math.cos(az), hr * math.sin(az)
    cz = CENTRE_Z - BEARING_DIST * math.cos(tilt)
    body -= Solid.make_sphere(POCKET_R, Plane(origin=(cx, cy, cz)))
# diagonal bottom pockets (original interface)
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
export_stl(body, os.path.join(OUT, "Nape-BallCase-34mm-stepped.stl"))
export_step(body, os.path.join(OUT, "Nape-BallCase-34mm-stepped.step"))
print("wrote STL + STEP to", OUT)
