#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 13:24:54 2024

@author: rafbar
"""

import laspy
import geopandas as gpd
from shapely.geometry import Point, box
import pandas as pd
import numpy as np
import os

os.chdir('shrub-height')

pols = gpd.read_file('data/interim/manual_pols.fgb')
pols = pols.to_crs("EPSG:32630")

shrub_points = pols.representative_point()

folder = 'data/raw/LiDAR/Leaf-On'
las_file_list = []
for file in os.listdir(folder):
    if file.endswith('.las'):
        las_file_list.append(file)

dirsave = 'data/interim/lidar_leafon_manual_id'

for fn in las_file_list:
    
    las_file_path = os.path.join(folder, fn)
    
    # Check if polygons are within bounds and skip if not
    with laspy.open(las_file_path) as meta:
        header = meta.header
        
        bbox = box(header.mins[0], header.maxs[0],  header.mins[1], header.maxs[1])
        points_in_check = shrub_points.within(bbox)
        
        block = las_file_path.split('_')[-1][:-4]
        
        if not any(points_in_check):
            print('Block ' + str(block) + ' not within field measurements bounds!')
            continue
    
    print('Opening block ' + str(block))
    las = laspy.read(las_file_path)
    
    print('Computing point locations')
    lasx = las.x
    lasy = las.y
    
    for _, pol in pols.iterrows():
        
        minx, miny, maxx, maxy = pol.geometry.bounds
        
        mask = (
                (lasx >= minx) & (lasx <= maxx) &
                (lasy >= miny) & (lasy <= maxy)
                )
        
        if mask.any():
            shrub_id = int(pol.id)
            print('Shrub {} within block! \n Computing measurements.'.format(shrub_id))
            
            image = las[mask]
            points = [Point(x, y) for x, y in zip(image.x, image.y)]
            las_gdf = gpd.GeoDataFrame({'return': image.return_number.array,
                                        'class': image.classification.array,
                                        'z': np.array(image.z),
                                        'R': (image.red / 65535 * 255).astype(np.uint8),
                                        'G': (image.green / 65535 * 255).astype(np.uint8),
                                        'B': (image.blue / 65535 * 255).astype(np.uint8),
                                        'geometry': points})
            las_gdf = las_gdf.set_crs('epsg:4326')
            las_gdf = las_gdf.clip(pol.geometry)
            las_gdf = las_gdf.to_crs('epsg:27700')
            
            las_gdf.to_file('{}/{}_b{}.fgb'.format(dirsave, shrub_id, block),
                            driver='FlatGeobuf')
            
            print('Processed {} \n'.format(shrub_id))

        
        