cd data

# Define common creation options
co_params="-of COG -co BLOCKSIZE=256 -co COMPRESS=DEFLATE -co PREDICTOR=3 -co BIGTIFF=YES"

gdaldem slope interim/dsm_sfm.tif interim/slp_sfm.tif -p -z 0.0001 $co_params