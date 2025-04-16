#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Process LiDAR point clouds at shrub locations.

This script extracts LiDAR points for manually identified shrub polygons.
"""

import argparse
import logging
import os
from pathlib import Path

import geopandas as gpd
import laspy
import numpy as np
from shapely.geometry import Point, box

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def process_las_file(
    las_file_path: str,
    shrub_points: gpd.GeoSeries,
    pols: gpd.GeoDataFrame,
    output_dir: str,
) -> None:
    """Process a single LAS file and extract points for each shrub polygon.

    Args:
        las_file_path: Path to LAS file
        shrub_points: GeoSeries of representative points for shrubs
        pols: GeoDataFrame containing shrub polygons
        output_dir: Directory to save output files
    """
    with laspy.open(las_file_path) as meta:
        header = meta.header
        bbox = box(header.mins[0], header.maxs[0], header.mins[1], header.maxs[1])
        points_in_check = shrub_points.within(bbox)

        block = Path(las_file_path).stem.split("_")[-1]

        if not any(points_in_check):
            logging.info(f"Block {block} not within field measurements bounds!")
            return

    logging.info(f"Opening block {block}")
    las = laspy.read(las_file_path)

    logging.info("Computing point locations")
    lasx = las.x
    lasy = las.y

    for _, pol in pols.iterrows():
        minx, miny, maxx, maxy = pol.geometry.bounds

        mask = (lasx >= minx) & (lasx <= maxx) & (lasy >= miny) & (lasy <= maxy)

        if mask.any():
            shrub_id = int(pol.id)
            logging.info(f"Shrub {shrub_id} within block! \nComputing measurements.")

            image = las[mask]
            points = [Point(x, y) for x, y in zip(image.x, image.y)]
            las_gdf = gpd.GeoDataFrame(
                {
                    "return": image.return_number.array,
                    "class": image.classification.array,
                    "z": np.array(image.z),
                    "R": (image.red / 65535 * 255).astype(np.uint8),
                    "G": (image.green / 65535 * 255).astype(np.uint8),
                    "B": (image.blue / 65535 * 255).astype(np.uint8),
                    "geometry": points,
                }
            )

            las_gdf = las_gdf.set_crs("epsg:4326")
            las_gdf = las_gdf.clip(pol.geometry)
            las_gdf = las_gdf.to_crs("epsg:27700")

            output_path = Path(output_dir) / f"{shrub_id}_b{block}.fgb"
            las_gdf.to_file(output_path, driver="FlatGeobuf")
            logging.info(f"Processed {shrub_id}\n")


def main(polygons_path: str, lidar_folder: str, output_dir: str) -> None:
    """Main function to process LiDAR data for shrub polygons.

    Args:
        polygons_path: Path to polygon file
        lidar_folder: Folder containing LAS files
        output_dir: Output directory for results
    """
    # Read and process polygons
    pols = gpd.read_file(polygons_path)
    pols = pols.to_crs("EPSG:32630")
    shrub_points = pols.representative_point()

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Process each LAS file
    lidar_path = Path(lidar_folder)
    las_files = list(lidar_path.glob("*.las"))

    for las_file in las_files:
        process_las_file(str(las_file), shrub_points, pols, output_dir)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Process LiDAR point clouds at shrub locations"
    )

    parser.add_argument(
        "--polygons",
        default="data/interim/manual_pols.fgb",
        help="Path to polygon file (default: %(default)s)",
    )

    parser.add_argument(
        "--lidar-folder",
        default="data/raw/LiDAR/Leaf-On",
        help="Folder containing LAS files (default: %(default)s)",
    )

    parser.add_argument(
        "--output-dir",
        default="data/interim/lidar_leafon_manual_id",
        help="Output directory for results (default: %(default)s)",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args.polygons, args.lidar_folder, args.output_dir)
