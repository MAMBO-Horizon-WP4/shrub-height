#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 12:17:05 2024

@author: rafbar
"""

import os
import argparse
import geopandas as gpd
import numpy as np


def calculate_statistics(points):
    """...existing docstring..."""
    stats = {}
    stats["mean"] = points.mean()
    stats["median"] = points.median()
    stats["std"] = points.std()
    stats["min"] = points.min()
    stats["max"] = points.max()
    stats["p10"] = points.quantile(0.1)
    stats["p90"] = points.quantile(0.9)
    return stats


def calculate_rmse(actual, predicted):
    return np.sqrt(np.mean((actual - predicted) ** 2))


def process_lidar_data(
    input_dir: str,
    polygons_path: str,
    output_path: str,
    src: str = "lidar_leafon",
    method: str = "field",
) -> None:
    """Process LiDAR data and calculate statistics.

    Args:
        input_dir: Directory containing the FGB files
        polygons_path: Path to polygons file
        output_path: Path to save output CSV
        src: Source identifier for LiDAR data
        method: Method identifier for processing
    """
    # DataFrame to store the results
    df = gpd.read_file(polygons_path)
    df = df.sort_values(by="id").reset_index(drop=True)
    df = df.drop("geometry", axis=1)

    # Loop through each file in the directory
    for filename in os.listdir(input_dir):
        if filename.endswith(".fgb"):
            filepath = os.path.join(input_dir, filename)

            # Read the FGB file
            gdf = gpd.read_file(filepath)

            # Extract the x and y coordinates from the geometry
            z_ground = gdf[gdf["class"] == 2].z
            z_canopy = gdf[gdf["class"] == 1].z

            # Calculate statistics
            stats_ground = calculate_statistics(z_ground)
            stats_canopy = calculate_statistics(z_canopy)

            # Combine stats and add the filename as the index
            stats_combined = {f"ground_{k}": v for k, v in stats_ground.items()}
            stats_combined.update({f"canopy_{k}": v for k, v in stats_canopy.items()})

            # Append the stats to the results DataFrame
            shrub_id = filename.split(".")[0].split("_")[0]
            df.loc[df.id == float(shrub_id), stats_combined.keys()] = (
                stats_combined.values()
            )

    df["h_lidar"] = (df.canopy_max - df.ground_max) * 100

    # Save the results to a CSV file
    df.to_csv(output_path)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Process LiDAR point clouds and calculate statistics"
    )

    parser.add_argument(
        "--input-dir",
        default="data/interim/lidar_leafon_field_id",
        help="Directory containing FGB files (default: %(default)s)",
    )

    parser.add_argument(
        "--polygons",
        default="data/interim/field_pols.fgb",
        help="Path to polygons file (default: %(default)s)",
    )

    parser.add_argument(
        "--output",
        default="data/processed/stats_field_lidar_leafon.csv",
        help="Output CSV path (default: %(default)s)",
    )

    parser.add_argument(
        "--source",
        default="lidar_leafon",
        help="Source identifier for LiDAR data (default: %(default)s)",
    )

    parser.add_argument(
        "--method",
        default="field",
        help="Method identifier for processing (default: %(default)s)",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    process_lidar_data(
        args.input_dir, args.polygons, args.output, args.source, args.method
    )
