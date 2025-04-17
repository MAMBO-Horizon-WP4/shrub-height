"""
Utility for generating test case samples
Which also shows working with project data from S3
"""

import geopandas as gpd
import rasterio
from rasterio.session import AWSSession
from dotenv import load_dotenv
import os
import logging

logging.basicConfig(level=logging.INFO)
load_dotenv()

s3_url = os.environ.get("AWS_ENDPOINT_URL", "")

session_options = {
    "AWS_VIRTUAL_HOSTING": False,
    "AWS_HTTPS": "YES",
    "AWS_S3_ENDPOINT": s3_url,
}

# Define this, with optional credentials, in .env in the root of this project

session = AWSSession(endpoint_url=s3_url)

# TODO: revisit the issue linked in the main block
# And see if we can get s3 prefix URLs working in the same way with Fiona as with Rasterio


def draw_bounds(filepath: str) -> tuple:
    """Load our shapefile with field measurements
    Draw a buffer around one of them, return the bounds"""
    shp = f"https://{s3_url}/{filepath}"
    logging.info(shp)
    gdf = gpd.read_file(shp)
    point = gdf.geometry.iloc[0]
    buffer_distance = 5  # meters
    buffered_geom = point.buffer(buffer_distance)

    # Get the bounds of the buffered geometry (returns tuple of (minx, miny, maxx, maxy))
    bounds = buffered_geom.bounds
    return bounds


def cut_dsm(filepath: str, outpath: str, bounds: list) -> None:
    data = []
    os.makedirs("../tests/data", exist_ok=True)
    with rasterio.Env(session=session, **session_options):
        with rasterio.open(filepath) as src:
            window = rasterio.windows.from_bounds(*bounds, transform=src.transform)
            kwargs = src.meta.copy()
            kwargs.update(
                {
                    "height": window.height,
                    "width": window.width,
                    "transform": rasterio.windows.transform(window, src.transform),
                }
            )
            logging.info(window)

            with rasterio.open(outpath, "w", **kwargs) as dst:
                dst.write(src.read(window=window))

                logging.info(f"wrote to {outpath}")


if __name__ == "__main__":
    # This works with a zipfile, but not with a .shp file
    # See https://github.com/geopandas/geopandas/issues/3129 for context
    bounds = draw_bounds("shrub-height/raw/Field_measurements/shrub_clean.zip")
    dsm = "s3://shrub-height/interim/dsm_sfm.tif"
    cut_dsm(dsm, "../tests/data/test_dsm.tif", bounds)
