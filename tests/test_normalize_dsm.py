import numpy as np
import rasterio
from shrubheight.prepro.normalize_dsm import normalize_dsm


def test_normalize_dsm(tmp_path):
    # Create test rasters
    dtm_data = np.ones((10, 10)) * 100
    dsm_data = np.ones((10, 10)) * 102  # 2m above ground

    transform = rasterio.transform.from_origin(0, 0, 1, 1)
    profile = {
        "driver": "GTiff",
        "dtype": "float32",
        "nodata": -9999,
        "width": 10,
        "height": 10,
        "count": 1,
        "crs": rasterio.crs.CRS.from_epsg(27700),
        "transform": transform,
    }

    dtm_path = tmp_path / "test_dtm.tif"
    dsm_path = tmp_path / "test_dsm.tif"
    output_path = tmp_path / "test_norm.tif"

    with rasterio.open(dtm_path, "w", **profile) as dst:
        dst.write(dtm_data, 1)
    with rasterio.open(dsm_path, "w", **profile) as dst:
        dst.write(dsm_data, 1)

    # Run normalization
    normalize_dsm(str(dtm_path), str(dsm_path), str(output_path))

    # Check output
    with rasterio.open(output_path) as src:
        result = src.read(1)
        assert np.allclose(
            result[result != -9999], 1.0
        )  # Should be 2m - 1m = 1m height
