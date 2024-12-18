# Shrub height estimation using SfM images

## Overview

Provide a concise description of the project's purpose, objectives, and the problem it addresses.    

## Usage

### Step 1: Data Pre-processing
**Description**: Fine tuned adjustments of the initial rasters and shapefiles to be better handled by the next phases. The DSM data from SfM was normalized using a 1m DTM from the EA (some further adjustments can be done in this phase, because the SfM data didn't seem to be perfectly aligned with the EA DTM).

### Step 2: Data Treatment
**Description**: The data from the LiDAR and SfM were collected at the manually identified shrub polygons. The LiDAR point clouds were used as ground truth, whereas the SfM DSM was used to collect stats at the polygons to get modelled height estimates further.

- **Aggregate LiDAR Point Clouds at individual shrubs**: `src/treatment/las_pc_at_shrubs.py`
-- input: 
-- output: 

- **Aggregate all input data**: `src/data_treatment/agg_att.py`
-- input:
-- output: 

- **Aggregated attributes to catchment accumulated**: `src/data_treatment/acc_att.py`
-- input:
-- output: 

### Step 3: Model Processing
- **Description**: Six ML models were processed. A K-fold CV was used at the gauging sites, and the all gauging data was used for all ungauged sites, for all models.

- **File**: `src/process_modelig/model_run.py`

## Project Structure

```bash
shrub-height/
├── data/              # data storage
├── src/               # Source code
├── .gitignore         # Git ignore file
├── README.md          # Project documentation
└── requirements.txt   # Python dependencies
```

## Contributing

If you welcome contributions, include guidelines on how others can contribute to the project.

## License

Specify the project's license to inform users of usage rights.