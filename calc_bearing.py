#!/usr/bin/env python3
"""calculate bearings from home to known NYC landmarks.
usage: python calc_bearing.py <lat> <lon>
example: python calc_bearing.py 45.614 -72.162
"""
import math
import sys

LANDMARKS = {
    "Brooklyn Bridge (tower)":  (40.7058, -73.9969),
    "Manhattan Bridge":         (40.7074, -73.9908),
    "Freedom Tower (1 WTC)":    (40.7127, -74.0134),
    "Empire State Building":    (40.7484, -73.9857),
    "Statue of Liberty":        (40.6892, -74.0445),
    "Brooklyn Navy Yard":       (40.7024, -73.9712),
    "LGA runway approach":      (40.7769, -73.8740),
    "JFK runway approach":      (40.6413, -73.7781),
    "EWR runway approach":      (40.6895, -74.1745),
    "Midtown (Times Square)":   (40.7580, -73.9855),
    "Hudson Yards":             (40.7536, -74.0003),
}


def bearing(lat1, lon1, lat2, lon2):
    lat1, lat2 = math.radians(lat1), math.radians(lat2)
    dlon = math.radians(lon2 - lon1)
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    return math.degrees(math.atan2(x, y)) % 360


def compass(deg):
    dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    return dirs[round(deg / 22.5) % 16]


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    lat = float(sys.argv[1])
    lon = float(sys.argv[2])

    print(f"\nhome: {lat}, {lon}\n")
    print(f"{'landmark':<30} {'bearing':>8} {'compass':>8}")
    print("-" * 50)

    results = []
    for name, (lt, ln) in LANDMARKS.items():
        b = bearing(lat, lon, lt, ln)
        results.append((b, name))

    for b, name in sorted(results):
        print(f"{name:<30} {b:>7.1f}° {compass(b):>8}")

    print("\n--- suggested config ---")
    print("# set WINDOW_BEARING to the center of your view")
    print("# set WINDOW_FOV to the total arc you can see")
    print("# from the photo: Brooklyn Bridge (left) to ~right edge of skyline")


if __name__ == "__main__":
    main()
