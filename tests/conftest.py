import os
import pytest
import numpy as np
import geopandas as gpd
import rasterio


@pytest.fixture
def fixture_dir():
    """
    Base directory for the test fixtures (images, metadata)
    """
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), "data/")


@pytest.fixture
def test_raster(tmp_path):
    """Create a test raster file."""
    data = np.random.rand(10, 10)
    transform = rasterio.transform.from_origin(0, 0, 1, 1)
    profile = {
        "driver": "GTiff",
        "dtype": "float32",
        "nodata": -9999,
        "width": 10,
        "height": 10,
        "count": 1,
        "crs": "EPSG:27700",
        "transform": transform,
    }

    path = tmp_path / "test.tif"
    with rasterio.open(path, "w", **profile) as dst:
        dst.write(data, 1)
    return path


@pytest.fixture
def test_dsm(fixture_dir):
    """Return a file path to real data sample dsm"""
    return os.path.join(fixture_dir, "test_dsm.tif")


@pytest.fixture
def test_gpd(fixture_dir):
    """Return a geopandas dataframe with a test observation"""
    # return gpd.read_file(os.path.join(fixture_dir, "shrub_sample.shp"))
    return gpd.read_file(os.path.join(fixture_dir, "field_pols.fgb"))
