import numpy as np
from build123d import *
from ocp_vscode import *
from bd_animation import AnimationGroup, clone, normalize_track

set_defaults(render_joints=True, helper_scale=8)

r = 100  # radius of the disk
d = 200  # distance from the center of the disk to the center of the arm
t = 5  # thickness of the parts
pr = 5  # radius of the pivot

# %%
pivot = Cylinder(pr, t)
disk = Cylinder(r + 2 * pr, t) - clone(pivot) + Pos(r, 0, t) * clone(pivot)
disk -= PolarLocations(0.6 * r, 6) * Cylinder(r / 6, t)

disk.color = "MediumAquaMarine"

RevoluteJoint(label="center", to_part=disk, axis=Axis.Z)
RevoluteJoint(label="pivot", to_part=disk, axis=Pos(r, 0, t).z_axis)

show(disk)

# %%

pivot_base = Cylinder(2 * pr, t)
base = Pos(d / 2, 0, 0) * Box(6 * pr + d, 6 * pr, t)
base = fillet(base.edges().filter_by(Axis.Z), 3)
base += Pos(d, 0, t) * pivot
base += Pos(0, 0, t) * pivot_base
base += Pos(0, 0, 2 * t) * pivot

base.color = "lightgray"

RigidJoint(label="disk_base", to_part=base, joint_location=Pos(d, 0, t))
RigidJoint(label="arm_base", to_part=base, joint_location=Pos(0, 0, 2 * t))

show(base)

# %%

slot = extrude(Pos(d, 0, 0) * SlotCenterToCenter(2 * r, 2 * pr), t, both=True)

arm = Pos((r + d) / 2, 0, 0) * Box(4 * pr + (r + d), 4 * pr, t)
arm = fillet(arm.edges().filter_by(Axis.Z), 3) - pivot - slot
arm.color = "orange"

RevoluteJoint(label="connect", to_part=arm, axis=Axis.Z)

show(arm)

# %%

disk_arm = AnimationGroup(
    children={"base": base, "disk": disk, "arm": arm},
    label="disk_arm",
    assemble=[
        ("base:disk_base", "disk:center"),
        ("base:arm_base", "arm:connect"),
    ],
)

show(disk_arm, render_joints=True)

# %%

show(disk_arm, render_joints=False)


def angle_arm(angle_disk):
    ra = np.deg2rad(angle_disk)
    v = np.array((d, 0)) + r * np.array((np.cos(ra), np.sin(ra)))
    return np.rad2deg(np.arctan2(v[1], v[0]))


animation = Animation(disk_arm)
n = 180
duration = 2
time_track = np.linspace(0, duration, n + 1)
disk_track = np.linspace(0, 360, n + 1)
arm_track = [angle_arm(a) for a in disk_track]

animation.add_track("/disk_arm/disk", "rz", time_track, normalize_track(disk_track))
animation.add_track("/disk_arm/arm", "rz", time_track, normalize_track(arm_track))

animation.animate(speed=1)
