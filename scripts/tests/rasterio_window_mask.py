"""Originally a test of reading a mask from a window vs a whole file.
The mask() interface wants a dataset object so that would involve
turning the window() back into a MemoryFile, feels overcomplicated.

Rasterio optimises well for mask reading so it's become a test of
performance improvement for a single open() and read every polygon
vs an open() each time through the loop
"""

import os
import rasterio
import geopandas as gpd
import rasterio.mask
import logging
import time
from tqdm import tqdm

from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)


def iter_read(src, geom):
    """Open every time"""
    logging.info(f"each {time.perf_counter()}")
    for row in tqdm(gdf.itertuples()):
        with rasterio.open(raster) as src:
            geom = row.geometry
            out_image, _ = rasterio.mask.mask(src, [geom], crop=True)


def main(filename: str, gdf: gpd.GeoDataFrame):
    iter_read(filename, gdf)
    pre_read(filename, gdf)


def pre_read(src, geom):
    """Open once"""
    logging.info(f"once {time.perf_counter()}")
    with rasterio.open(raster) as src:
        for row in tqdm(gdf.itertuples()):
            geom = row.geometry
            out_image, _ = rasterio.mask.mask(src, [geom], crop=True)


if __name__ == "__main__":
    raster = "s3://shrub-height/interim/sfm_normalized.tif"
    tabular = "s3://shrub-height/interim/field_pols.fgb"
    # Just read the first 10 rows
    gdf = gpd.read_file(tabular).iloc[0:10]
    # Get the mask for the first record, with and without a window; time it
    main(raster, gdf)
