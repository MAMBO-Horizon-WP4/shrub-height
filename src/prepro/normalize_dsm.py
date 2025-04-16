#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 13 19:44:10 2024

@author: rafbar
"""

import argparse
from pathlib import Path
import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import calculate_default_transform, reproject


def normalize_dsm(
    dtm_path: str, dsm_path: str, output_path: str, target_crs: str = "EPSG:27700"
) -> None:
    """Normalize Digital Surface Model using Digital Terrain Model.

    Args:
        dtm_path: Path to Digital Terrain Model file
        dsm_path: Path to Digital Surface Model file
        output_path: Path to save normalized DSM
        target_crs: Target coordinate reference system
    """
    # Read the reference DTM
    with rasterio.open(dtm_path) as dtm:
        dtm_array = dtm.read(1)  # Read the first band
        dtm_transform = dtm.transform
        dtm_crs = dtm.crs

        # Open the DSM file
        with rasterio.open(dsm_path) as dsm:
            ref_array = dsm.read(1)
            transform, width, height = calculate_default_transform(
                dsm.crs, target_crs, dsm.width, dsm.height, *dsm.bounds
            )

            kwargs = dsm.meta.copy()
            kwargs.update(
                {
                    "crs": target_crs,
                    "transform": transform,
                    "width": width,
                    "height": height,
                }
            )

            # Create empty array for reprojected reference raster
            dst_array = np.empty((height, width), dtype=rasterio.float32)

            # Reproject DSM
            dsm_array, _ = reproject(
                source=ref_array,
                destination=dst_array.copy(),
                src_transform=dsm.transform,
                src_crs=dsm.crs,
                dst_transform=transform,
                dst_crs=target_crs,
                dst_nodata=dsm.nodata,
                resampling=Resampling.nearest,
            )

            # Reproject DTM
            dtm_rep, _ = reproject(
                source=dtm_array,
                destination=dst_array.copy(),
                src_transform=dtm_transform,
                src_crs=dtm_crs,
                dst_transform=transform,
                dst_crs=target_crs,
                resampling=Resampling.nearest,
            )

            # Calculate normalized DSM
            result_array = dsm_array - (dtm_rep + 1)
            result_array[dsm_array == dsm.nodata] = dsm.nodata

            # Save result
            with rasterio.open(output_path, "w", **kwargs) as out:
                out.write(result_array, 1)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Normalize Digital Surface Model using Digital Terrain Model"
    )

    parser.add_argument(
        "--dtm",
        default="data/raw/EA_1m/TL06sw_DTM_1m.tif",
        help="Path to DTM file (default: %(default)s)",
    )

    parser.add_argument(
        "--dsm",
        default="data/raw/SfM/StrawDSM_SfM_L1-geoid_apr24.tif",
        help="Path to DSM file (default: %(default)s)",
    )

    parser.add_argument(
        "--output",
        default="data/interim/sfm_normalized.tif",
        help="Output path (default: %(default)s)",
    )

    parser.add_argument(
        "--crs",
        default="EPSG:27700",
        help="Target coordinate system (default: %(default)s)",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # Ensure output directory exists
    output_dir = Path(args.output).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    normalize_dsm(
        dtm_path=args.dtm,
        dsm_path=args.dsm,
        output_path=args.output,
        target_crs=args.crs,
    )
