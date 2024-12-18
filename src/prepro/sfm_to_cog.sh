cd data

# Define common creation options
co_params="-of COG -co BLOCKSIZE=256 -co COMPRESS=DEFLATE -co PREDICTOR=2 -co BIGTIFF=YES"

# gdalwarp -t_srs EPSG:27700 raw/SfM/StrawDSM_SfM_L1-geoid_apr24.tif $co_params interim/dsm_sfm.tif

gdalwarp -t_srs EPSG:27700 raw/SfM/strawberry_ortho_terraSfM_L1_apr24.tif $co_params interim/rgb_sfm.tif