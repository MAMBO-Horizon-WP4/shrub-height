from shrubheight.treatment.shrub_stats_sfm import get_raster_stats, process_data


def test_get_raster_stats(test_dsm, test_gpd):
    # Create test polygon
    # Create test raster files
    raster_files = [test_dsm]  # Mock file paths

    for row in test_gpd.itertuples():
        stats = get_raster_stats(row, raster_files)
        assert isinstance(stats, dict)

        expected_keys = [
            "mean",
            "median",
            "std",
            "min",
            "max",
            "25th_percentile",
            "75th_percentile",
        ]
        assert all(f"sfm_{key}" in stats for key in expected_keys)


def test_process_data(fixture_dir, tmp_path, lidar_path):
    process_data(fixture_dir, "field", tmp_path, lidar_path)
