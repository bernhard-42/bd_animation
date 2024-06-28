import copy
import numpy as np

import anytree
from build123d import *


def clone(obj, color=None, origin=None):
    new_obj = copy.copy(obj)

    if origin is not None:
        new_obj.location = origin.inverse() * new_obj.location

    if color is not None:
        new_obj.color = color

    return new_obj


def normalize_track(points):
    start = np.array(points[0])
    return [(point - start).tolist() for point in points]


class AnimationGroup(Compound):
    def __init__(self, children, label, assemble=None):
        # Assign names to labels
        for l, obj in children.items():
            obj.label = l

        # Assemble the parts
        # Note: this needs top be done before adding the parts to the Compound
        for s, t in assemble or []:
            path, joint_name = s.split(":")
            obj = children[path]
            joint = obj.joints[joint_name]

            to_path, to_joint_name = t.split(":")
            to_obj = children[to_path]
            to_joint = to_obj.joints[to_joint_name]

            joint.connect_to(to_joint)

        super().__init__(label=label, children=list(children.values()))

    def __getitem__(self, path):
        """Get a part by path."""
        resolver = anytree.Resolver("label")
        name, _, rest = path.strip("/").partition("/")
        if name != self.label:
            raise ValueError(f"Path '{path}' not valid")
        elif rest == "":
            return self

        return resolver.get(self, rest)
