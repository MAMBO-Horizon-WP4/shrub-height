from shrubheight.treatment.shrub_stats_sfm import get_raster_stats


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
        assert all(f"test_{key}" in stats for key in expected_keys)
