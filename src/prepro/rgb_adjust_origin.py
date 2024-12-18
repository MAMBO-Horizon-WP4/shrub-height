from osgeo import gdal

# Input and output paths
input_path = "data/raw/SfM/strawberry_ortho_terraSfM_L1_apr24.tif"
shifted_path = "data/interim/shifted_raster.tif"
output_path = "data/interim/rgb_sfm.tif"

# Open the source raster
src_ds = gdal.Open(input_path)
if src_ds is None:
    raise FileNotFoundError(f"Could not open {input_path}")

# Get the original GeoTransform and adjust it
geo_transform = list(src_ds.GetGeoTransform())
geo_transform[0] -= 1  # Shift west
geo_transform[3] -= 1  # Shift south

# Apply the adjusted GeoTransform
driver = gdal.GetDriverByName("GTiff")
shifted_ds = driver.Create(shifted_path, src_ds.RasterXSize, src_ds.RasterYSize, src_ds.RasterCount, src_ds.GetRasterBand(1).DataType)

# Copy metadata, projection, and adjusted GeoTransform
shifted_ds.SetProjection(src_ds.GetProjection())
shifted_ds.SetGeoTransform(tuple(geo_transform))

# Copy raster bands
for i in range(1, src_ds.RasterCount + 1):
    band = src_ds.GetRasterBand(i)
    shifted_ds.GetRasterBand(i).WriteArray(band.ReadAsArray())
shifted_ds = None  # Save and close

# Reproject to EPSG:27700 with creation options
gdal.Warp(
    output_path,
    shifted_path,
    dstSRS="EPSG:27700",
    format="COG",
    creationOptions=[
        "BLOCKSIZE=256",
        "COMPRESS=DEFLATE",
        "PREDICTOR=2",
        "BIGTIFF=YES"
    ],
)

print(f"Adjusted, reprojected, and saved to {output_path}")
