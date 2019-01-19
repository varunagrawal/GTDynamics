#!/usr/bin/env python
"""
Test forward dynamics using factor graphs.
Author: Frank Dellaert and Mandy Xie
"""

# pylint: disable=C0103, E1101, E0401

from __future__ import print_function

import math

from denavit_hartenberg import DenavitHartenberg, Link
from gtsam import Point3, Pose3, Rot3

# Denavit-Hartenberg parameters for RR manipulator
RR_calibration = DenavitHartenberg(
    [Link(0, 0, 2, 0, 'R', 1, Point3(1, 0, 0), [0, 1/6., 1/6.]),
     Link(0, 0, 2, 0, 'R', 1, Point3(1, 0, 0), [0, 1/6., 1/6.])],
    base=Pose3(), tool=Pose3(Rot3.Ry(math.radians(90)), Point3(0, 0, 0))
)

# Denavit-Hartenberg parameters for PUMA manipulator
PUMA_calibration = DenavitHartenberg(
    [Link(0, 0.0000, 0.0000, +90, 'R', 0, Point3(0, 0, 0), [0, 0, 0.35]),
     Link(0, 0.0000, 0.4318, 0.0, 'R', 17.40, Point3(
         0.068, 0.006, -0.016), [0.130, 0.524, 0.539]),
     Link(0, 0.1500, 0.0203, -90, 'R', 4.80,
          Point3(0, -0.070, 0.014), [0.066, 0.0125, 0.086]),
     Link(0, 0.4331, 0.0000, +90, 'R', 0.82,
          Point3(0, 0, -0.019), [0.0018, 0.0018, 0.00130]),
     Link(0, 0.0000, 0.0000, -90, 'R', 0.34,
          Point3(0, 0, 0), [0.00030, 0.00030, 0.00040]),
     Link(0, 0.0000, 0.0000, 0.0, 'R', 0.09, Point3(0, 0, 0.032), [0.00015, 0.00015, 0.00004])],
    base=Pose3(), tool=Pose3(Rot3.Ry(math.radians(90)), Point3(0, 0, 0))
)
