# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 09:32:00 2024

@author: RafBar
"""

import os
import argparse
from pathlib import Path
import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.mask import mask


def compute_Ps(dname: str, data: np.ndarray) -> np.ndarray:
    """Compute percentiles of data at regular intervals.

    Args:
        dname: Name of the data source
        data: Array of values to compute percentiles for

    Returns:
        Array of percentile values
    """
    step = 5
    percentiles = np.arange(step, 101, step)
    return np.percentile(data, percentiles)


def compute_stats(dname: str, data: np.ndarray) -> dict:
    """Calculate statistical measures for input data.

    Args:
        dname: Name of the data source
        data: Array of values to compute statistics for

    Returns:
        Dictionary of computed statistics
    """
    stats_result = {}
    stats_result[dname + "_mean"] = data.mean()
    stats_result[dname + "_std"] = data.std()
    stats_result[dname + "_min"] = data.min()  # np.percentile(data, [1])[0]
    stats_result[dname + "_max"] = data.max()  # np.percentile(data, [99])[0]
    stats_result[dname + "_25th_percentile"] = np.percentile(data, [25])[0]
    stats_result[dname + "_median"] = np.percentile(data, [50])[0]
    stats_result[dname + "_75th_percentile"] = np.percentile(data, [75])[0]
    return stats_result


def get_raster_stats(polygon: gpd.GeoDataFrame, raster_files: list) -> dict:
    """Extract and compute statistics from raster data for a given polygon.

    Args:
        polygon: GeoDataFrame row containing polygon geometry
        raster_files: List of paths to raster files

    Returns:
        Dictionary of computed statistics
    """
    stats_d = {}
    print(polygon.id)
    for raster_file in raster_files:
        dname = raster_file.split("/")[-1].split("_")[-2]
        with rasterio.open(raster_file) as src:
            # If the polygon intersects the bounding box of the raster
            if not rasterio.coords.disjoint_bounds(src.bounds, polygon.geometry.bounds):
                print(raster_file)
                # Read the raster data that overlaps with the polygon
                out_image, out_transform = mask(src, [polygon.geometry], crop=True)

                if src.count >= 3:
                    red, green, blue = out_image[:3].astype(float)
                    data = (green - red) / (green + red - blue + 1e-6)
                    data = data[data <= 1]
                else:
                    no_data = src.nodata
                    data = out_image[out_image != no_data]

                print(data.mean())
                # Store the results
                if (data.size > 0) & (data.mean() != 0):
                    stats_d = compute_stats(dname, data)
                    # break
    return stats_d


def process_data(input_dir: str, method: str, output_dir: str) -> None:
    """Process SfM data and calculate statistics for polygons.

    Args:
        input_dir: Directory containing input files
        method: Processing method identifier
        output_dir: Directory for output files
    """
    data_files = [
        os.path.join(input_dir, f)
        for f in os.listdir(input_dir)
        if f.startswith("sfm_normalized") and f.endswith(".tif")
    ]

    pols_path = Path(input_dir) / f"{method}_pols.fgb"
    pols = gpd.read_file(pols_path)
    pols = pols.sort_values(by="id").reset_index(drop=True)

    stats_list = []
    for _, row in pols.iterrows():
        stats = get_raster_stats(row, data_files)
        stats["id"] = int(row.id)
        stats_list.append(stats)

    df = pd.DataFrame(stats_list)

    # Get validation height from lidar
    lidar_path = Path(output_dir) / f"stats_{method}_lidar_leafon.csv"
    h_lidar = pd.read_csv(lidar_path, index_col=0)

    df[["area", "h_lidar"]] = h_lidar[["area", "h_lidar"]]
    df.set_index("id", inplace=True)

    output_path = Path(output_dir) / f"shrubs2ml_{method}.csv"
    df.to_csv(output_path)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Process SfM data and calculate statistics"
    )

    parser.add_argument(
        "--input-dir",
        default="data/interim",
        help="Directory containing input files (default: %(default)s)",
    )

    parser.add_argument(
        "--method",
        default="field",
        help="Processing method identifier (default: %(default)s)",
    )

    parser.add_argument(
        "--output-dir",
        default="data/processed",
        help="Output directory (default: %(default)s)",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    process_data(
        input_dir=args.input_dir, method=args.method, output_dir=args.output_dir
    )
