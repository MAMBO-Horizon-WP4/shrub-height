"""
Convert point measurements to polygon geometries using buffer radius from field data.
"""

import argparse
import geopandas as gpd


def create_circle(row):
    """Create circular buffer around point using diameter from measurements.

    Args:
        row: GeoDataFrame row containing:
            - geometry: Point geometry in centimeters
            - d_mean: Mean diameter in centimeters

    Returns:
        Circular polygon geometry in meters

    Raises:
        ValueError: If d_mean appears to be in centimeters (>5m is unlikely for shrubs)
    """
    diameter = row["d_mean"]

    # Validation - warn if diameter seems too large (likely wrong units)
    if diameter > 500:  # 5m diameter would be very large for a shrub
        raise ValueError(
            f"Diameter {diameter}m seems too large. Check if input is in meters not centimeters."
        )

    radius = diameter / 2
    return row["geometry"].buffer(radius)


def process_points(input_path: str, output_path: str, epsg: str = "EPSG:27700") -> None:
    """Process point measurements and create polygon buffers.

    Args:
        input_path: Path to input point shapefile
        output_path: Path to save output polygon file
        epsg: Target coordinate system EPSG code
    """
    # Load and reproject input points
    df = gpd.read_file(input_path)
    df = df.to_crs(epsg)

    # Create circular buffers
    df["geometry"] = df.apply(create_circle, axis=1)
    df["area"] = df.area

    # Select output columns
    df = df[["id", "species", "area", "h_mean", "geometry"]]

    # Save to FlatGeobuf format
    df.to_file(output_path, driver="FlatGeobuf")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert point measurements to polygon geometries"
    )

    parser.add_argument(
        "--input",
        default="data/raw/Field_measurements/shrub_clean.shp",
        help="Input point shapefile path (default: %(default)s)",
    )

    parser.add_argument(
        "--output",
        default="data/interim/field_pols.fgb",
        help="Output polygon file path (default: %(default)s)",
    )

    parser.add_argument(
        "--epsg",
        default="EPSG:27700",
        help="Target coordinate system (default: %(default)s)",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    process_points(args.input, args.output, args.epsg)
