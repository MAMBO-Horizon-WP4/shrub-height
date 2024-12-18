#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 12:17:05 2024

@author: rafbar
"""

import os
import numpy as np
import geopandas as gpd
import pandas as pd

os.chdir('shrub-height')

def calculate_statistics(points):
    stats = {}
    stats['mean'] = points.mean()
    stats['median'] = points.median()
    stats['std'] = points.std()
    stats['min'] = points.min()
    stats['max'] = points.max()
    stats['p10'] = points.quantile(0.1)
    stats['p90'] = points.quantile(0.9)
    return stats

def calculate_rmse(actual, predicted):
    return np.sqrt(np.mean((actual - predicted) ** 2))

# Directory containing the FGB files
directory = 'data/interim/lidar_leafon_manual_id'

# DataFrame to store the results
df = gpd.read_file('data/interim/manual_pols.fgb')
df = df.sort_values(by='id').reset_index(drop=True)
df = df.drop('geometry', axis=1)

# Loop through each file in the directory
for filename in os.listdir(directory):
    if filename.endswith('.fgb'):
        filepath = os.path.join(directory, filename)
        
        # Read the FGB file
        gdf = gpd.read_file(filepath)
        
        # Extract the x and y coordinates from the geometry
        z_ground = gdf[gdf['class']==2].z
        z_canopy = gdf[gdf['class']==1].z
        
        # Calculate statistics for x and y coordinates
        stats_ground = calculate_statistics(z_ground)
        stats_canopy = calculate_statistics(z_canopy)
        
        # Combine stats and add the filename as the index
        stats_combined = {f'ground_{k}': v for k, v in stats_ground.items()}
        stats_combined.update({f'canopy_{k}': v for k, v in stats_canopy.items()})
        
        # Append the stats to the results DataFrame
        shrub_id = filename.split('.')[0].split('_')[0]
        df.loc[df.id==float(shrub_id), stats_combined.keys()] = stats_combined.values()

df['h_lidar'] = (df.canopy_max - df.ground_max)*100

# Compare with field measurements (for field data)
# df['h_diff'] = df.h_lidar - df.h_mean
# calculate_rmse(df.h_mean, df.h_lidar)
# df[['h_mean', 'h_lidar']].corr(method='pearson')

# Save the results to a CSV file
df.to_csv('data/processed/stats_manual_lidar_leafon.csv')




