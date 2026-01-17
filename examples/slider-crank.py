from build123d import *
from ocp_vscode import *
from bd_animation import *
import numpy as np

set_defaults(reset_camera=Camera.TOP, render_joints=True)

# %%
u_len = 4
l_len = 2
width = 1
radius = 2
thickness = 0.1
hole = 0.2
tol = 1e-2


def create_knob():
    return extrude(Circle(hole - tol), 2 * thickness)


def create_rod(length):
    sk = SlotCenterToCenter(2 * length, width)
    sk -= Pos(-length, 0, 0) * Circle(hole)
    rod = extrude(sk, thickness)
    rod += Pos(length, 0, thickness) * create_knob()
    RevoluteJoint("hole", rod, Axis((-length, 0, 0), (0, 0, 1)))
    RigidJoint("knob", rod, Pos(length, 0, thickness))
    return rod


def create_disc(radius):
    sk = Circle(radius)
    disc = extrude(sk, thickness)
    RevoluteJoint("disc", disc, Axis.Z)
    disc += Pos(radius - 0.5, 0, thickness) * create_knob()
    RigidJoint(
        "knob",
        disc,
        Pos(radius - 0.5, 0, thickness),
    )
    return disc


u_rod = create_rod(u_len)
u_rod.label = "u_rod"
u_rod.color = "#84c775"

l_rod = create_rod(l_len)
l_rod.label = "l_rod"
l_rod.color = "#3fa45d"

disc = create_disc(radius)
disc.label = "disc"
disc.color = "#0a764e"

show(u_rod, l_rod, disc)

# %%

# Create a "local coord-system" for the upper rod
# since it needs to be animate separately
ag_u_rod = AnimationGroup(
    children={
        # Set the animation origin for u_rod to the hole
        "u_rod": clone(u_rod, origin=Pos(-u_len, 0, 0)),
    },
    label="u_rod",
)
# Since we aligned the animation origin with, the joint
# of the assembly is now at (0, 0, 0)
RigidJoint("hole", ag_u_rod, Pos(0, 0, 0))

show(ag_u_rod)

# %%
# Create a "local coordinate system" for the assembly of both rods
# since they need to be animated together
ag_rods = AnimationGroup(
    children={
        "u_rod": ag_u_rod,
        # Set the animation origin for l_rod to the hole
        "l_rod": clone(l_rod, origin=Pos(-l_len, 0, 0)),
    },
    label="rods",
    # Mind the order: we assemble lower rod onto upper rod
    assemble=[("l_rod:knob", "u_rod:hole")],
)
# Since we aligned the animation origin with, the joint
# of the assembly is now at (0, 0, 0)
RigidJoint("hole", ag_rods, Pos(0, 0, 0))

show(ag_rods)

# %%
# Create a "local coordinate system" for the whole assembly
a_all = AnimationGroup(
    children={
        "disc": disc,
        "rods": ag_rods,
    },
    label="all",
    # Mind the order: we assemble rods onto disc
    assemble=[("disc:knob", "rods:hole")],
)
show(Rot(0, 0, 90) * a_all, render_joints=True)

anim = Animation(a_all)

N = 100
# 2 seconds for one full turn
times = np.linspace(0, 2, N)
alpha = np.linspace(0, 360, N)

# Apply law of sines (https://en.wikipedia.org/wiki/Law_of_sines) to the triangle
# (disc_center - disc_knob) / l_rod / (disc…center - l_rod_knob)
sin_alpha = (radius - 0.5) * np.sin(np.radians(alpha)) / (2 * l_len)
gamma = np.degrees(np.arcsin(np.clip(sin_alpha, -1, 1)))
beta = -gamma - alpha

anim.add_track("/all", "rz", times, alpha)
anim.add_track("/all/rods", "rz", times, beta)
anim.add_track("/all/rods/u_rod", "rz", times, gamma)

anim.animate(1)
# %%
