#!/usr/bin/env python3
import cv2
import numpy as np


def get_trapezoid_to_rectangle_transform(trapezoid_corners):
    """
    Calculates the perspective transformation matrix to map a trapezoid to a rectangle.

    Args:
        trapezoid_corners (list of tuples): A list of four (x, y) tuples
                                            representing the corners of the trapezoid.

    Returns:
        numpy.ndarray: The 3x3 transformation matrix.
        tuple: The width and height of the destination rectangle.
    """
    corners = np.array(trapezoid_corners, dtype="float32")

    # Sort by y-coordinate to separate top and bottom rows based on cartesian coordinates (y grows up)
    y_sorted = corners[np.argsort(corners[:, 1])]

    bottom_row = y_sorted[:2]
    top_row = y_sorted[2:]

    # Sort rows by x-coordinate to find tl, tr, bl, br
    bottom_row = bottom_row[np.argsort(bottom_row[:, 0])]
    top_row = top_row[np.argsort(top_row[:, 0])]

    bl, br = bottom_row
    tl, tr = top_row

    src_corners = np.array([tl, tr, br, bl], dtype="float32")

    # Compute the width of the new rectangle
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    # Compute the height of the new rectangle
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    # Define destination corners to preserve orientation (y increases upwards)
    # tl, tr, br, bl -> (0,h), (w,h), (w,0), (0,0)
    dst_corners = np.array(
        [[0, maxHeight - 1], [maxWidth - 1, maxHeight - 1], [maxWidth - 1, 0], [0, 0]],
        dtype="float32",
    )

    # Compute the perspective transform matrix
    matrix = cv2.getPerspectiveTransform(src_corners, dst_corners)

    return matrix, (maxWidth, maxHeight)


def transform_points(points, matrix):
    """
    Applies a perspective transformation to a list of points.

    Args:
        points (list of tuples): A list of (x, y) points to transform.
        matrix (numpy.ndarray): The 3x3 transformation matrix.

    Returns:
        numpy.ndarray: An array of transformed points.
    """
    points_np = np.array([points], dtype=np.float32)
    transformed_points = cv2.perspectiveTransform(points_np, matrix)
    return transformed_points[0]


def rectify_points(
    points, trapezoid_corners=[(255, 334), (363, 335), (350, 86), (313, 86)]
):
    """
    A single function to transform points from a trapezoidal area to a rectangular one.

    Args:
        points (list of tuples): A list of (x, y) points to transform.
        trapezoid_corners (list of tuples): A list of four (x, y) tuples
                                            representing the corners of the trapezoid.

    Returns:
        numpy.ndarray: An array of transformed points.
        tuple: The width and height of the destination rectangle.
    """
    transform_matrix, (width, height) = get_trapezoid_to_rectangle_transform(
        trapezoid_corners
    )
    transformed_points = transform_points(points, transform_matrix)
    return transformed_points, (width, height)
