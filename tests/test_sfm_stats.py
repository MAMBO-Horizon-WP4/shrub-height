from shrubheight.treatment.shrub_stats_sfm import get_raster_stats, process_data


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
