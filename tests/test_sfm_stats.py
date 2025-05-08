import os
import pytest
from pathlib import Path
from shrubheight.treatment.shrub_stats_sfm import (
    get_raster_stats,
    process_data,
    find_input_rasters,
)

nos3access = pytest.mark.skipif(
    os.environ.get("AWS_ENDPOINT_URL") is None, reason="s3 endpoint not set"
)


def test_get_raster_stats(test_dsm, test_gpd):
    # Create test polygon
    # Create test raster files
    raster_files = [test_dsm]  # Mock file paths

    stats = get_raster_stats(test_gpd, raster_files)
    assert isinstance(stats[0], dict)

    expected_keys = [
        "mean",
        "median",
        "std",
        "min",
        "max",
        "25th_percentile",
        "75th_percentile",
    ]
    assert all(f"sfm_{key}" in stats[0] for key in expected_keys)


def test_process_data(fixture_dir, tmp_path, test_lidar_path):
    process_data(fixture_dir, "field", tmp_path, lidar_path=test_lidar_path)


@nos3access
def test_find_input_rasters(fixture_dir):
    """Check local and s3 file listing behaves the same way
    Won't run if AWS_ENDPOINT_URL is not set"""
    local = find_input_rasters(fixture_dir)
    s3 = find_input_rasters("s3://shrub-height/interim/")
    assert len(local) > 0
    assert len(s3) > 0
    assert Path(local[0]).name == Path(s3[0]).name
