# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 09:32:00 2024

@author: RafBar
"""

import os
import argparse
from pathlib import Path
from typing import NamedTuple, Optional
import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.mask import mask
import s3fs
from tqdm import tqdm


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


def get_raster_stats(polygons: gpd.GeoDataFrame, raster_files: dict) -> dict:
    """Extract and compute statistics from raster data for a given polygon.

    Args:
        polygons: a GeoDataFrame containing polygon geometry
        raster_files: dict of raster file data
            name : { bounds : (tuple)
                     path: str }

    Returns:
        Dictionary of computed statistics
    """
    stats = []

    for filename in raster_files:
        # TODO - depending on file naming conventions brittle
        # It's better if we pass in a dict here - more flexible later too
        dname = file_shortname(filename)
        with rasterio.open(filename) as src:

            for polygon in tqdm(polygons.itertuples()):
                stats_d = {}

                # If the polygon intersects the bounding box of the raster
                if not rasterio.coords.disjoint_bounds(
                    src.bounds, polygon.geometry.bounds
                ):
                    # Read the raster data that overlaps with the polygon
                    data = get_masked_raster(src, polygon)
                    if (data.size > 0) & (data.mean() != 0):
                        stats_d = compute_stats(dname, data)
                        stats_d["id"] = int(polygon.id)
                        stats.append(stats_d)

    return stats


def get_masked_raster(src: rasterio.DatasetReader, polygon: NamedTuple):
    """
    Read the image bands within a polygon mask
    If it's 3 band, return a binary array of all values that aren't nodata
    If its more than 3 band, return a binary array of all values that are <1 where
    (green - red) / (green + red - blue + 1e-6)
    Note: add an explanation of why this is!
    """
    out_image, _ = mask(src, [polygon.geometry], crop=True)

    if src.count >= 3:
        red, green, blue = out_image[:3].astype(float)
        data = (green - red) / (green + red - blue + 1e-6)
        data = data[data <= 1]
    else:
        no_data = src.nodata
        data = out_image[out_image != no_data]

    return data


def file_shortname(raster_file: str) -> str:
    """
    Utility to extract a short alias for an input file
    Better to use a catalogue or index for this than rely on naming conventions!
    """
    return raster_file.split("/")[-1].split("_")[-2]


def find_input_rasters(input_dir: str) -> list:
    """Given a directory, identify rasters to use as input.
    Currently specifically matches `sfm_normalized` (output of previous stage)
    Could be made more generic in future!
    """
    files = []
    if input_dir.startswith("s3"):
        s3 = s3fs.S3FileSystem()
        files = s3.ls(input_dir)

    else:
        files = os.listdir(input_dir)

    return [
        os.path.join(input_dir, f)
        for f in files
        if f.startswith("sfm_normalized") and f.endswith(".tif")
    ]


def process_data(
    input_dir: str, method: str, output_dir: str, lidar_path: Optional[str] = None
) -> None:
    """Process SfM data and calculate statistics for polygons.

    Args:
        input_dir: Directory containing input files
        method: Processing method identifier (One of "field" or "manual")
        output_dir: Directory for output files
    """
    # Checks for dsm_ and sfm_ prefixed files in a single directory.
    # Revisit this interface if scaling up! Pass in a list, or a filename that has a list in it
    # Intermediate issue here is s3 filename matching

    data_files = find_input_rasters(input_dir)

    # Note - this was pathlib.Path but that truncates s3:// URLs, throws errors
    # This should work with either s3 or local filesystem paths
    pols_path = os.path.join(input_dir, f"{method}_pols.fgb")
    pols = gpd.read_file(pols_path)
    pols = pols.sort_values(by="id").reset_index(drop=True)

    stats_list = get_raster_stats(pols, data_files)

    df = pd.DataFrame(stats_list)

    # Get validation height from lidar
    # Option to supply a path, or default to output from previous stage
    if not lidar_path:
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
