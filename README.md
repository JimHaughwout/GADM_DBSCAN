# dbscan_gadm
Fun with DBSCAN algorithm and GADM-geocoded points of interest.

This reads in a data set of coordinates (latitude and longitude) along with 
geocoded [Global Administrative Area](http://www.gadm.org/) features
for these, then performs unsupervised learning to cluster these into 
zones of interest based on geographic features using the 
[Density-Based Spatial Clustering of Applications with Noise](https://en.wikipedia.org/wiki/DBSCAN) 
algorithm with a customized distance function.

## Options
Currently the program defines options in a [`settings.py`](https://github.com/JimHaughwout/gadm_scan/blob/master/settings.py) file:

#### General Settings
Setting | Description | Values
----------------|-------------|-------
`INPUT_FILE` | Source data file of coordinates | See below
`OUTPUT_FILE` | Output data file name | Qualified filename with path
`ZOA_SUMMARY_TO_SCREEN` | Print ZOA summary to screen | `True`, `False`
`MATPLOT_ZOA_CLUSTERS` | Use `matplotlib` to graph clusters | `True`, `False`
`GADM_MODE` | Use GADM features to modify Vicenty distance. See below. | `True`, `False`
`DEFAULT_RADIUS` | Default ZOA radius for DBSCAN epsilon, in km | `1.0`
`DEFAULT_ROUNDING` | Default rounding in decimal places, for GPS coordinates. | `4`
`LOCAL` | Adjustment factor for coordinates in same  neighborhood* | `0.4`
`X_TOWN` | Adjustment factor for coordinates in same city* | `2.0`

*When Adjustment Factor is > 1 it is a penalty (<1 is a bonus). Both are combined.
For example, we default 2x as penalty for cross-town transit but scale this back
60% (to 1.2) if both points are in the same neighborhood.

#### Specific CSV File Settings
TODO. Sample is [here]](https://github.com/JimHaughwout/gadm_scan/blob/master/data/points_of_interest.csv) 

#### Usage
'git clone` and run from the command line:
```sh
$ python dbscan_gadm_metric.py
```

## Note On Custom Calculation
TODO about replacement