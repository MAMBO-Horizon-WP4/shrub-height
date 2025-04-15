import geopandas as gpd

# Load the input shapefile
df = gpd.read_file("data/raw/Manually_labeled/reprojected_yellow_low_shrub.shp")
df = df.to_crs("EPSG:27700")

df.id = df.index + 1
df.area = df.geometry.area

df.to_file("data/interim/manual_pols.fgb", driver="FlatGeobuf")
