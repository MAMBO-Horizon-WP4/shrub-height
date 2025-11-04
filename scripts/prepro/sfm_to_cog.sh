# Conversion into Cloud Optimised GeoTIFF

input_file=${1:-raw/SfM/StrawDSM_SfM_L1-geoid_apr24.tif}
output_file=${2:-interim/rgb_sfm.tif}

echo $input_file

echo $output_file
# Define common creation options
co_params="-of COG -co BLOCKSIZE=256 -co COMPRESS=DEFLATE -co PREDICTOR=2 -co BIGTIFF=YES"

gdalwarp -t_srs EPSG:27700 $input_file $co_params $output_file
