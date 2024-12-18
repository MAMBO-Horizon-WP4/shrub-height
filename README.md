# Shrub height estimation using SfM images

## Overview

Provide a concise description of the project's purpose, objectives, and the problem it addresses.    

## Usage

### Step 1: Data Pre-processing

**Description**: Fine tuned adjustments of the initial rasters and shapefiles to be better handled by the next phases. The DSM data from SfM was normalized using a 1m DTM from the EA (some further adjustments can be done in this phase, because the SfM data didn't seem to be perfectly aligned with the EA DTM).

### Step 2: Data Treatment
**Description**: The data from the LiDAR and SfM were collected at the manually identified shrub polygons. The LiDAR point clouds were used as ground truth, whereas the SfM DSM was used to collect stats at the polygons to get modelled height estimates further.

- **Aggregate LiDAR Point Clouds (PCs) at individual shrubs**: `src/treatment/las_pc_at_shrubs.py`
    - input: 
        - indivudal shrub polygons file
        - point clouds files directory (raw)
    - output: 
        - one file per individual shrub containing point clouds

- **Collect Ground Truth Heights from the individual PCs**: `src/treatment/shrub_stats_las.py`
    - input: 
        - indivudal shrub polygons file
        - directory with individual point clouds (PCs)
    - output: 
        - csv containing lidar PC stats at individuals and a processed height estimate as ground truth, defined as the difference between the max first and last returns

- **Collect SfM statistics at individual shrubs and get ready for modelling**: `src/data_treatment/shrub_stats_sfm.py`
    - input:
        - indivudal shrub polygons file
        - SfM image file
        - csv with ground truth height from previous step
    - output: 
        - csv with all stats necessary for the height modelling

### Step 3: Model Processing
**Description**: Four ML models were processed. A K-fold CV was used.

- **Functions for the ML processing approach**: `src/modelling/utils.py`

- **Model Run**: `src/modelling/utils.py`

## Project Structure

```bash
shrub-height/
├── data/              # data storage
├── src/               # Source code
├── .gitignore         # Git ignore file
├── README.md          # Project documentation
└── requirements.txt   # Python dependencies
```

## License

MIT
