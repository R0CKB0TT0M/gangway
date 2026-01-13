#!/usr/bin/env python3
"""
Project points from image space to floor space
"""

import numpy as np

from ..config import DST_POINTS, SRC_POINTS


def get_homography(src=np.array(SRC_POINTS), dst=np.array(DST_POINTS)):
    """
    Berechnet die 3x3 Homographie-Matrix.
    src, dst: Jeweils 4 Punkte als (4, 2) array.
    """
    A = []
    for i in range(4):
        x, y = src[i]
        u, v = dst[i]
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y])

    A = np.array(A)
    B = dst.flatten()

    # Löse Ax = B für die 8 Parameter (h33 wird als 1 angenommen)
    h = np.linalg.solve(A, B)
    return np.append(h, 1).reshape(3, 3)


DEFAULT_TRANSFORM = get_homography()


def apply_transform(points, M=DEFAULT_TRANSFORM):
    """
    Wendet die Matrix M auf eine Liste von Punkten an.
    points: (N, 2) array
    """
    # In homogene Koordinaten umwandeln (x, y) -> (x, y, 1)
    points_homo = np.pad(points, ((0, 0), (0, 1)), constant_values=1)

    # Transformation: P' = M * P
    transformed = points_homo @ M.T

    # Normalisierung (Division durch w-Komponente)
    return transformed[:, :2] / transformed[:, 2, np.newaxis]
