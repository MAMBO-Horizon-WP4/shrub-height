import pytest
import numpy as np
import rasterio


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
