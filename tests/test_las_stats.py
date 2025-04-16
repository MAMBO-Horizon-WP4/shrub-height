import geopandas as gpd
from shapely.geometry import Polygon
from shrubheight.treatment.shrub_stats_sfm import get_raster_stats


def test_get_raster_stats():
    # Create test polygon
    polygon = gpd.GeoDataFrame(
        {"geometry": [Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])], "id": [1]}
    ).iloc[0]

    # Create test raster files
    raster_files = ["test_dsm.tif"]  # Mock file paths

    stats = get_raster_stats(polygon, raster_files)
    assert isinstance(stats, dict)
    expected_keys = ["mean", "median", "std", "min", "max", "p10", "p90"]
    assert all(
        f"{prefix}_{key}" in stats
        for prefix in ["ground", "canopy"]
        for key in expected_keys
    )
