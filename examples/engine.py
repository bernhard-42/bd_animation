# %%%
import math

import numpy as np
from build123d import *
from ocp_vscode import *
from ocp_vscode.animation import Animation

from bd_animation import AnimationGroup, clone, normalize_track

set_defaults(helper_scale=8, render_joints=False, reset_camera=Camera.RESET)

# %% Load the engine assembly
# https://grabcad.com/library/engine-assembly-77
a_engine = import_step("Engine Assembly.stp")

rod_con = Compound(
    a_engine.children[0].children[0].wrapped, label="rod_con", color=Color(0x696969)
)
rod_con.location = Location()
rod_cap = Compound(
    a_engine.children[0].children[1].wrapped, label="rod_cap", color=Color(0x696969)
)
rod_cap.location = Location()
piston_pin = Compound(
    a_engine.children[0].children[2].wrapped, label="piston_pin", color=Color(0x000000)
)
piston_pin.location = Location()
crankshaft = Compound(
    a_engine.children[1].wrapped, label="crankshaft", color=Color(0xC0C0C0)
)
engine_block = Compound(
    a_engine.children[2].wrapped, label="engine_block", color=Color(0x778899)
)
piston_head = Compound(
    a_engine.children[3].wrapped, label="piston_head", color=Color(0xC0C0C0)
)
piston_head.location = Location()

show(
    Location((-400, 200, 0), (0, 0, 180)) * engine_block,
    Pos(120, 0, 0) * rod_con,
    Pos(200, 0, 0) * rod_cap,
    Pos(0, 100, 0) * crankshaft,
    Pos(300, 0, 0) * piston_pin,
    Pos(300, 80, 0) * piston_head,
)

# %% Rod AnimationGroup

e = rod_cap.edges().filter_by(GeomType.CIRCLE).group_by(Axis.Y)[0].sort_by()
c = (e[2] + e[3]).center()
loc = Location(list(c), (0, 0, 180))

RigidJoint(label="connect", to_part=rod_con, joint_location=Pos(*c))
RigidJoint(label="connect", to_part=rod_cap, joint_location=loc)

rod = AnimationGroup(
    children={"rod_con": rod_con, "rod_cap": rod_cap},
    label="rod",
    assemble=[("rod_con:connect", "rod_cap:connect")],
)

c = rod.faces().filter_by(GeomType.CYLINDER).sort_by(Axis.Y)[-2].center()
c.Z = 0
rod_axis = Axis(list(c), (1, 0, 0))
rod_loc = rod_axis.location
j = RevoluteJoint(label="center_top", to_part=rod, axis=rod_axis)

show(rod, j.symbol)

# %% Piston AnimationGroup

holes = piston_head.faces().filter_by(GeomType.CYLINDER).group_by()[2]
r = holes[0].edges().filter_by(GeomType.CIRCLE)[0].radius
pos = (0, 0, r + holes[0].center().Z)
loc = Location(pos, (90, 0, 180))

RigidJoint(label="connect", to_part=piston_pin, joint_location=Rot(0, 90, 90))
RigidJoint(label="connect", to_part=piston_head, joint_location=loc)
piston = AnimationGroup(
    children={
        "piston_head": clone(piston_head, origin=loc),
        "piston_pin": clone(piston_pin),
    },
    label="piston",
    assemble=[("piston_head:connect", "piston_pin:connect")],
)
j = RigidJoint(label="pin", to_part=piston, joint_location=Location())

show(piston, j.symbol)

# %% Rod connected to piston AnimationGroup

rod_piston = AnimationGroup(
    children={
        "rod": clone(rod, origin=Axis.X.location),
        "piston": clone(piston, origin=Pos(pos)),
    },
    label="rod_piston",
    assemble=[("rod:center_top", "piston:pin")],
)
j = RevoluteJoint(label="center_bot", to_part=rod_piston, axis=Axis.Z)

show(rod_piston, j.symbol)

# %% Crankshaft AnimationGroup
crankshaft = Rot(*crankshaft.location.orientation).inverse() * crankshaft

c_locs = []
for i, (x, y) in enumerate(((-350, 40), (-250, -40), (-150, -40), (-50, 40))):
    f = crankshaft.faces().filter_by(GeomType.CYLINDER).sort_by_distance((x, 0, y))
    c = f[0] + f[1]
    l = Location(c.center(), (0, 90, -90))
    c_locs.append(l)
    RigidJoint(label=f"pin_{i}", to_part=crankshaft, joint_location=l)

children = {"crankshaft": clone(crankshaft)}
children.update({f"rod_piston_{i}": clone(rod_piston) for i in range(4)})
crank = AnimationGroup(
    children=children,
    label="crankshaft",
    assemble={
        ("crankshaft:pin_0", "rod_piston_0:center_bot"),
        ("crankshaft:pin_1", "rod_piston_1:center_bot"),
        ("crankshaft:pin_2", "rod_piston_2:center_bot"),
        ("crankshaft:pin_3", "rod_piston_3:center_bot"),
    },
)

j = RevoluteJoint(label="axis", to_part=crank, axis=Axis((0, 0, 0), (1, 0, 0)))

show(crank, j.symbol)

# %% Engine block and crankshaft AnimationGroup

engine_block.location = Rot(0, 0, 180)
RigidJoint(label="connect", to_part=engine_block, joint_location=Rot(0, -90, 0))

engine = AnimationGroup(
    children={"engine_block": engine_block, "crankshaft": crank},
    label="engine",
    assemble=[("engine_block:connect", "crankshaft:axis")],
)

show(engine)

# %%

animation = Animation(engine)

radius = abs(c_locs[0].position.Z)
rod_length = abs(rod.joints["center_top"].location.position.Y)

duration = 2
crank_track = []
piston_track = [[], [], [], []]
rod_track = [[], [], [], []]

time_track = np.linspace(0, duration, 181)

for a in np.linspace(0, 360, 180 + 1):
    crank_track.append(a)

for i in range(4):
    origin = c_locs[i].position
    for a in np.linspace(0, 360, 180 + 1):
        alpha = a + 90 if i in [0, 3] else a - 90

        l1 = radius * math.sin(math.radians(alpha))
        l0 = radius * math.cos(math.radians(alpha))
        l2 = math.sqrt(rod_length**2 - l0**2)
        beta = math.degrees(math.atan2(l2, l0))

        offset = 180 if i in [0, 3] else 0
        gamma = offset - alpha - beta
        delta = 90 - beta
        rod_track[i].append(gamma)
        piston_track[i].append(-delta)

animation.tracks = []
animation.add_track(
    f"/engine/crankshaft", "rx", time_track, normalize_track(crank_track)
)
for i in range(4):
    animation.add_track(
        f"/engine/crankshaft/rod_piston_{i}",
        "rz",
        time_track,
        normalize_track(rod_track[i]),
    )
    animation.add_track(
        f"/engine/crankshaft/rod_piston_{i}/piston",
        "rz",
        time_track,
        normalize_track(piston_track[i]),
    )

animation.animate(2)
