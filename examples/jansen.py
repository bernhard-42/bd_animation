# %%
import numpy as np
from build123d import *
from ocp_vscode import *

from bd_animation import AnimationGroup, clone, normalize_track

set_defaults(render_joints=True, helper_scale=8, reset_camera=Camera.KEEP)


# %% Helpers


def intersect(p0, r0, p1, r1):
    """
    Bourke's algorithm (http://paulbourke.net/geometry/circlesphere)
    to find intersect points of circle0 (p0, r0) and circle1 (p1, r1)
    """
    p10 = p1 - p0
    d = np.linalg.norm(p10)
    if (d > r0 + r1) or (d < abs(r1 - r0)) or ((d == 0) and (r0 == r1)):
        raise RuntimeError("No intersection")

    a = (r0**2 - r1**2 + d**2) / (2 * d)
    h = np.sqrt(r0**2 - a**2)
    p2 = p0 + (a / d) * p10
    r = np.array([-p10[1], p10[0]]) * (h / d)

    return (p2 - r, p2 + r)


# %% Model

R = 2
T = 1


length, level, color = {}, {}, {}

length[(1, 2)] = 15.0
length[(2, 3)] = 50.0
length[(3, 4)] = 55.8
length[(4, 0)] = 40.1
length[(0, 3)] = 41.5
length[(4, 6)] = 39.4
length[(0, 5)] = 39.3
length[(2, 5)] = 61.9
length[(5, 6)] = 36.7
length[(6, 7)] = 65.7
length[(7, 5)] = 49.0

level[(0, 3, 4)] = T
level[(5, 6, 7)] = T
level[(1, 2)] = T
level[(2, 3)] = 2 * T
level[(2, 5)] = 0
level[(4, 6)] = 2 * T
level[(0, 5)] = 2 * T

color[(0, 3, 4)] = "Red"
color[(5, 6, 7)] = "RoyalBlue"
color[(1, 2)] = "DarkBlue"
color[(2, 3)] = "DarkGreen"
color[(2, 5)] = "Orange"
color[(4, 6)] = "Purple"
color[(0, 5)] = "OliveDrab"

ids = [(0, 3, 4), (5, 6, 7), (1, 2), (2, 3), (2, 5), (4, 6), (0, 5)]


def triangle(id, points):
    """Create an AnimationGroup of triangle with the given id and points"""

    p1, p2, p3 = [points[i] for i in id]
    t = Polyline(p1, p2, p3, p1)
    f = make_face(t)
    f = offset(f, R)
    f -= Pos(p1) * Circle(R / 2) + Pos(p2) * Circle(R / 2) + Pos(p3) * Circle(R / 2)
    t = extrude(f, T)
    t = Pos(0, 0, level[id]) * t
    t.color = color[id]

    group = AnimationGroup(
        # ensure that the object is relocated to p1 as the origin
        children={f"link{id}": clone(t, origin=Pos(p1))},
        label=f"leg{id}",
    )
    # and then relocate the parent back to p1
    group.loc = Pos(p1)

    return group


def link(id, points):
    """Create an AnimationGroup of link with the given id and points"""

    p1, p2 = [points[i] for i in id]
    s = SlotCenterPoint((p1 + p2) / 2, p1, 2 * R)
    s -= Pos(p1) * Circle(R / 2) + Pos(p2) * Circle(R / 2)
    s = extrude(s, T)
    s = Pos(0, 0, level[id]) * s
    s.color = color[id]

    group = AnimationGroup(
        # ensure that the object is relocated to p1 as the origin
        children={f"link{id}": clone(s, origin=Pos(p1))},
        label=f"link{id}",
    )
    # and then relocate the parent back to p1
    group.loc = Pos(p1)

    return group


def linkage(alpha):
    """For a given angle return the 2d location of each joint and the link angles"""

    def angle(p1, p2):
        return 180 + np.degrees(np.arctan2(p1[1] - p2[1], p1[0] - p2[0]))

    alpha = np.radians(alpha)

    points = [0] * 8
    points[0] = np.array([0, 0])
    points[1] = np.array([38.0, 7.8])
    points[2] = points[1] + length[(1, 2)] * np.array([np.cos(alpha), np.sin(alpha)])
    points[3] = intersect(points[0], length[(0, 3)], points[2], length[(2, 3)])[1]
    points[4] = intersect(points[0], length[(4, 0)], points[3], length[(3, 4)])[1]
    points[5] = intersect(points[0], length[(0, 5)], points[2], length[(2, 5)])[0]
    points[6] = intersect(points[4], length[(4, 6)], points[5], length[(5, 6)])[0]
    points[7] = intersect(points[5], length[(7, 5)], points[6], length[(6, 7)])[1]

    angles = {}
    for id in ids:
        i, j = id[:2] if len(id) == 3 else id
        angles[id] = angle(points[i], points[j])

    return points, angles


points, angles = linkage(alpha=0)

base = Polyline(points[0], (points[1][0], 0), points[1])

jansen = AnimationGroup(
    children={
        "base": clone(base, color="Gray"),
        f"link{ids[0]}": triangle(ids[0], points),
        f"link{ids[1]}": triangle(ids[1], points),
        f"link{ids[2]}": link(ids[2], points),
        f"link{ids[3]}": link(ids[3], points),
        f"link{ids[4]}": link(ids[4], points),
        f"link{ids[5]}": link(ids[5], points),
        f"link{ids[6]}": link(ids[6], points),
    },
    label="jansen",
)

dirs = ((5, 5), (6, 0), (-6, 0), (0, -6), (6, 0), (-6, 4), (6, 2), (-6, 4))

vertices = [Pos(p - dirs[i]) * Text(str(i), 8) for i, p in enumerate(points)]
for i, v in enumerate(vertices):
    v.label = f"p({i})"

axis = []
for id, a in angles.items():
    p = PolarLine(points[id[0]], 10, a)
    p.label = f"angle({id})"
    axis.append(p)

show(jansen, vertices, axis)


# %%
show(jansen)

animation = Animation(jansen)
n = 18
duration = 2
time_track = np.linspace(0, duration, n + 1)

names = [c.label for c in jansen.children]

position_track = {id: [] for id in ids}
angle_track = {id: [] for id in ids}

for alpha in np.linspace(0, 360, n + 1):
    points, angles = linkage(alpha)
    for id in ids:
        p0 = points[id[0]]
        position_track[id].append((p0[0], p0[1], level[id]))
        angle_track[id].append(angles[id])

for id in ids:
    name = f"/jansen/link{id}"

    # make sure to normalize each track, i.e. subtract the first point from every point
    animation.add_track(name, "t", time_track, normalize_track(position_track[id]))
    animation.add_track(name, "rz", time_track, normalize_track(angle_track[id]))

animation.animate(speed=1)
