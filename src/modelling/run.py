
import os
os.chdir('shrub-height')

import numpy as np
import pandas as pd
from src.modelling import utils as mlp # make sure it is added to path


df = pd.read_parquet('data/processed/shrubs2ml.parquet')
df = df.dropna()

# Choose target
targets = ['h_lidar'] 
models = ['MLR', 'SVM', 'GBM', 'RF'] 
features = df.columns.drop(targets)

df = df.sample(frac = 1) # Shuffle values MAKES ALL THE DIFFERENCE IDKW
for target in targets:
    if df[target].isna().any():
        method = 'dataset'
        selected_features = features
    else:
        method = 'k-fold'
        # Select features for modelling based on hyerarchical clustering
        cluster_feature, selected_features = mlp.fs_hcluster(df,
                                                              features, 
                                                              target, 
                                                              cluster_threshold=0.3, 
                                                              plot=True)
    X = df[selected_features].values
    y = df[target].values
    
    for mlmodel in models:
        print('Running for ' + target + ' and ' + mlmodel)
        yhat, imps = mlp.model_run(X,
                                  y,
                                  mlmodel,
                                  method=method,
                                  )
        
        try:
            imps.columns = selected_features
            mlp.plot_results(y, yhat, imps, target, mlmodel, savefigs=False)
        except:
            mlp.accuracy(y, yhat)
        
        # Creating the DataFrame with specified columns and errors
        dfr = pd.DataFrame(index=df.index)
        dfr['obs'] = y
        dfr['pred'] = yhat
        
        imps.to_parquet('data/output/imps_'+target+'_'+mlmodel+'_'+method+'.parquet')
        dfr.to_parquet('data/output/results_raw_'+target+'_'+mlmodel+'_'+method+'.parquet')
        
        
        
    

