#!/usr/bin/env python3
import csv

import homgraphic_projection
import matplotlib.pyplot as plt

INPUT_FILE = "positions.csv"
OUTPUT_FILE = "positions.png"


def plot_positions():
    points = []

    with open(INPUT_FILE, "r") as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            points.append((int(row[0]), int(row[1])))

    transformed_points = homgraphic_projection.apply_transform(points)

    # Use NumPy slicing to select columns for x and y coordinates
    x_coords = transformed_points[:, 0]
    y_coords = transformed_points[:, 1]

    plt.figure(figsize=(4, 10))  # Adjusted for a more vertical aspect ratio
    plt.scatter(x_coords, y_coords, s=5)
    plt.xlabel("X Coordinate (Transformed)")
    plt.ylabel("Y Coordinate (Transformed)")
    plt.title("Scatter Plot of Transformed XOVIS Positions")
    plt.grid(True)
    plt.axis("equal")

    plt.savefig(OUTPUT_FILE)
    print(f"Plot saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    plot_positions()
