import geopandas as gpd
from shapely.geometry import Polygon
from shrubheight.treatment.shrub_stats_sfm import get_raster_stats


def test_get_raster_stats(test_dsm, test_gpd):
    # Create test polygon
    # Create test raster files
    raster_files = [test_dsm]  # Mock file paths

    stats = get_raster_stats(test_gpd, raster_files)
    assert isinstance(stats, dict)
    print(stats)
    expected_keys = ["mean", "median", "std", "min", "max", "p10", "p90"]
    assert all(
        f"{prefix}_{key}" in stats
        for prefix in ["ground", "canopy"]
        for key in expected_keys
    )
