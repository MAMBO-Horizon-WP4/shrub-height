#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 13 19:44:10 2024

@author: rafbar
"""

import os
import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import reproject, calculate_default_transform

dtm_path = 'data/raw/EA_1m/TL06sw_DTM_1m.tif'
folder_path = 'data/raw/SfM'
dsm_path = 'data/raw/SfM/StrawDSM_SfM_L1-geoid_apr24.tif'
output_folder = 'data/interim'


# Read the reference TIFF
with rasterio.open(dtm_path) as dtm:
    dtm_array = dtm.read(1)  # Read the first band
    dtm_transform = dtm.transform
    dtm_crs = dtm.crs
    
    # Loop through all TIFF files in the specified folder
    # for filename in os.listdir(folder_path):
    #     if filename.startswith('Strawberry_DSM_') and filename.endswith('.tif'):
            # dsm_path = os.path.join(folder_path, filename)
    
    # Open the current TIFF file in the loop
    with rasterio.open(dsm_path) as dsm:
        ref_array = dsm.read(1)
        target_crs = 'EPSG:27700'
        transform, width, height = calculate_default_transform(
                    dsm.crs, target_crs, dsm.width, dsm.height, *dsm.bounds)

        kwargs = dsm.meta.copy()
        kwargs.update({
            'crs': target_crs,
            'transform': transform,
            'width': width,
            'height': height
        })
        
        # Create an empty array for the reprojected reference raster
        dst_array = np.empty((height, width), dtype=rasterio.float32)

        dsm_array, _ = reproject(
            source=ref_array,
            destination=dst_array.copy(),
            src_transform=dsm.transform,
            src_crs=dsm.crs,
            dst_transform=transform,
            dst_crs=target_crs,
            dst_nodata=dsm.nodata,
            resampling=Resampling.nearest
        )
        
        # Reproject the reference raster directly to match the current TIFF file
        dtm_rep, _ = reproject(
            source=dtm_array,
            destination=dst_array.copy(),
            src_transform=dtm_transform,
            src_crs=dtm_crs,
            dst_transform=transform,
            dst_crs=target_crs,
            resampling=Resampling.nearest
        )
        
        # Perform the array operation
        
        result_array = dsm_array - (dtm_rep + 1)
        result_array[dsm_array==dsm.nodata] = dsm.nodata
        
        # Prepare to save the resulting raster
        output_path = os.path.join(output_folder, "sfm_normalized.tif")

        with rasterio.open(output_path, 'w', **kwargs) as out:
            out.write(result_array, 1)  # Write the first band


