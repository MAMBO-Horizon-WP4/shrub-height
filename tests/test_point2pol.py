import pytest
import geopandas as gpd
import numpy as np
from shapely.geometry import Point
from shrubheight.prepro.point2pol import create_circle, process_points


def test_create_circle():
    """Test circle creation with diameter in meters"""
    point = gpd.GeoDataFrame(
        {"geometry": [Point(0, 0)], "d_mean": [200]}  # 200cm diameter
    ).iloc[0]

    circle = create_circle(point)
    expected_area = np.pi * 1e4  # πr² where r=1m
    assert circle.area == pytest.approx(expected_area, rel=1e-2)


def test_create_circle_validates_units():
    """Test that large diameters (likely in cm) are caught"""
    point = gpd.GeoDataFrame(
        {"geometry": [Point(0, 0)], "d_mean": [20000]}  # 200m would be huge!
    ).iloc[0]

    with pytest.raises(ValueError, match="seems too large"):
        create_circle(point)


def test_process_points(tmp_path):
    # Create test input data
    points = gpd.GeoDataFrame(
        {
            "geometry": [Point(0, 0), Point(1, 1)],
            "d_mean": [100, 200],
            "id": 1,
            "species": ["A", "B"],
            "h_mean": [1.5, 2.0],
        }
    )
    points.set_crs(epsg=4326, inplace=True)
    input_path = tmp_path / "test_points.shp"
    output_path = tmp_path / "test_output.fgb"
    points.to_file(input_path)

    # Run processing
    process_points(str(input_path), str(output_path))

    # Check output
    result = gpd.read_file(output_path)
    assert len(result) == 2
    assert all(col in result.columns for col in ["id", "species", "area", "h_mean"])
