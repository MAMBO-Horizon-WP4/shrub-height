# Shrub height estimation using SfM images

## Overview

A series of Python scripts to process LiDAR point clouds and SfM images at polygons identified as shrub masses, and estimate the height of the vegetation using Machine Learning algorithms.

## Usage

### Step 1: Data Pre-processing

**Description**: Fine tuned adjustments of the initial rasters and shapefiles to be better handled by the next phases. The DSM data from SfM was normalized using a 1m DTM from the EA (some further adjustments can be done in this phase, because the SfM data didn't seem to be perfectly aligned with the EA DTM).

### Step 2: Data Treatment
**Description**: The data from the LiDAR and SfM were collected at the manually identified shrub polygons. The LiDAR point clouds were used as ground truth, whereas the SfM DSM was used to collect stats at the polygons to get modelled height estimates further.

- **Aggregate LiDAR Point Clouds (PCs) at individual shrubs**: `src/treatment/las_pc_at_shrubs.py`
    - input: 
        - indiviudal shrub polygons file
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
## Installation

### Install GDAL

This will vary according to your platform. For Debian/Ubuntu, it's like this, and gives you version 3.6.2:

`sudo apt install gdal-bin`

#### GDAL without root access

The cleanest way to do this is to use the GDAL version that comes pre-built with `conda`. In which case follow these instructions to create a python environment with `miniconda` and install GDAL that way

```
conda create -n shrubheight python=3.8
conda activate shrubheight
conda install -c conda-forge proj=9.2 proj-data=1.12
conda install -c conda-forge gdal=3.7
conda install -c conda-forge geopandas rasterio
```

### Create python environment and install dependencies

The versions of GDAL and of its python bindings need to match. Thus `pyproject.toml` is currently pinned to 3.6.2

```
python -m venv .venv
source .venv/bin/activate
```

Now install our package and its dependencies:

```
pip install -e .[dev,test]
```


## Run with DVC

### Preprocessing

This assumes you have the project raw data in `data/raw` and an empty directory in `data/interim`.
Change into the `prepro` directory and run `dvc repro`.

```
cd prepro
dvc repro
```

_Note - until we've got shared storage established, working copy of `data/raw` is on an external drive mounted in this directory, I've done this:_

```
cd prepro
ln -s /media/zool/mounted_drive/mambo_data/Projs/mambo-dl/shrub-height/data/raw raw
mkdir interim
dvc repro
```

## License

MIT
