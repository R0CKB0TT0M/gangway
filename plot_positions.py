#!/usr/bin/env python3
import csv

import matplotlib.pyplot as plt

INPUT_FILE = "positions.csv"
OUTPUT_FILE = "positions.png"


def plot_positions():
    x_coords = []
    y_coords = []

    with open(INPUT_FILE, "r") as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            x_coords.append(int(row[0]))
            y_coords.append(int(row[1]))

    plt.figure(figsize=(5, 5))
    plt.scatter(x_coords, y_coords, s=5)
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.title("Scatter Plot of XOVIS Positions")
    plt.grid(True)
    plt.axis("equal")
    plt.savefig(OUTPUT_FILE)
    print(f"Plot saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    plot_positions()
