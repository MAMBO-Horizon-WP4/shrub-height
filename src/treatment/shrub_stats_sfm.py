# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 09:32:00 2024

@author: RafBar
"""

import os
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.mask import mask

os.chdir('shrub-height')

def compute_Ps(dname, data):
    stats_result = {}
    step = 5
    percentiles = np.arange(step, 101, step)
    return np.percentile(data, percentiles)

def compute_stats(dname, data):
    stats_result = {}
    stats_result[dname+'_mean'] = data.mean()
    stats_result[dname+'_std'] = data.std() 
    stats_result[dname+'_min'] = data.min() # np.percentile(data, [1])[0]
    stats_result[dname+'_max'] = data.max() # np.percentile(data, [99])[0]
    stats_result[dname+'_25th_percentile'] = np.percentile(data, [25])[0]
    stats_result[dname+'_median'] = np.percentile(data, [50])[0]
    stats_result[dname+'_75th_percentile'] = np.percentile(data, [75])[0]
    return stats_result

def get_raster_stats(polygon, raster_files):
    stats_d = {}
    print(polygon.id)
    for raster_file in raster_files:
        dname = raster_file.split('/')[-1].split('_')[-2]
        with rasterio.open(raster_file) as src:
            # If the polygon intersects the bounding box of the raster
            if not rasterio.coords.disjoint_bounds(src.bounds, polygon.geometry.bounds):
                print(raster_file)
                # Read the raster data that overlaps with the polygon
                out_image, out_transform = mask(src, [polygon.geometry], crop=True)
                
                if src.count >= 3:
                    red, green, blue = out_image[:3].astype(float)
                    data = (green - red) / (green + red - blue + 1e-6)
                    data = data[data <= 1]
                else:
                    no_data = src.nodata
                    data = out_image[out_image != no_data]
                
                print(data.mean())
                # Store the results
                if (data.size > 0) & (data.mean() != 0):
                    stats_d = compute_stats(dname, data)
                    # break
    return stats_d

directory = 'data/interim'
data_files = [os.path.join(directory, f) for f in os.listdir(directory)
                if f.startswith("sfm_normalized") and 
                f.endswith(".tif")]

pols = gpd.read_file("data/interim/manual_pols.fgb")
pols = pols.sort_values(by='id').reset_index(drop=True)

stats_list = []
for index, row in pols.iterrows():
    stats = get_raster_stats(row, data_files)
    stats['id'] = int(row.id)
    stats_list.append(stats)
    

df = pd.DataFrame(stats_list)

# Get validation height from lidar
h_lidar = pd.read_csv('data/processed/stats_manual_lidar_leafon.csv', index_col=0)

df[['area', 'h_lidar']] = h_lidar[['area', 'h_lidar']]

df.set_index('id', inplace=True)

df.to_parquet('data/processed/shrubs2ml.parquet')
    
    
    
    
    
    
    
