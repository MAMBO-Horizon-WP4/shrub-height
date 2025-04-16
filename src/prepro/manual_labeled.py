"""
Process manually labeled shrub polygons and save to FlatGeobuf format.
"""

import argparse
from pathlib import Path
import geopandas as gpd


def process_polygons(
    input_path: str, output_path: str, target_crs: str = "EPSG:27700"
) -> None:
    """Process manually labeled polygons and compute areas.

    Args:
        input_path: Path to input shapefile
        output_path: Path to save processed polygons
        target_crs: Target coordinate reference system
    """
    # Load and reproject input polygons
    df = gpd.read_file(input_path)
    df = df.to_crs(target_crs)

    # Add sequential IDs and compute areas
    df.id = df.index + 1
    df.area = df.geometry.area

    # Save to FlatGeobuf format
    df.to_file(output_path, driver="FlatGeobuf")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Process manually labeled shrub polygons"
    )

    parser.add_argument(
        "--input",
        default="data/raw/Manually_labeled/reprojected_yellow_low_shrub.shp",
        help="Input shapefile path (default: %(default)s)",
    )

    parser.add_argument(
        "--output",
        default="data/interim/manual_pols.fgb",
        help="Output file path (default: %(default)s)",
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

    process_polygons(args.input, args.output, args.crs)
