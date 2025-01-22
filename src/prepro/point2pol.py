
import geopandas as gpd

# Load the input shapefile
df = gpd.read_file("data/raw/Field_measurements/shrub_clean.shp")
df = df.to_crs('EPSG:27700')

def create_circle(row):
    radius = row['d_mean'] / 100
    return row['geometry'].buffer(radius)

df['geometry'] = df.apply(create_circle, axis=1)
df['area'] = df.area

df = df[['id', 'species', 'area', 'h_mean', 'geometry']]

df.to_file("data/interim/field_pols.fgb", driver='FlatGeobuf')
