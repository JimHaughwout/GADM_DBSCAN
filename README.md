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

### General Settings
Setting | Description | Example Values
----------------|-------------|-------
`INPUT_FILE` | Source data file of coordinates | See below
`OUTPUT_FILE` | Output data file name | Qualified filename with path
`ZOA_SUMMARY_TO_SCREEN` | Print ZOA summary to screen | `True`, `False`
`MATPLOT_ZOA_CLUSTERS` | Use `matplotlib` to graph clusters | `True`, `False`
`MODE` | Custom distance metric formula to use. See below. | See below
`DEFAULT_RADIUS` | Default ZOA radius for DBSCAN epsilon, in km | `1.0`
`DEFAULT_ROUNDING` | Default rounding in decimal places, for GPS coordinates. | `4`
`LOCAL`* | Adjustment factor for coordinates in same  neighborhood | `0.4`
`X_TOWN`* | Adjustment factor for coordinates in same city | `2.0`

*These are settings are ignored in `vicenty-basic` mode (see below)
When Adjustment Factor is > 1 it is a penalty (<1 is a bonus). Both are combined.
For example, we default 2x as penalty for cross-town transit but scale this back
60% (to 1.2) if both points are in the same neighborhood.

#### Custom Distance Metric Modes
You can use one of three modes to calculation the distance between points for
DBSCAN clustering

##### `vicenty-basic` Mode
Custom distance metric using [Vincenty's Formula](https://en.wikipedia.org/wiki/Vincenty%27s_formulae).

##### `vicenty-gadm` Mode
Custom distance metric that combines Vincenty's Formula with GADM features
to calculate a scored distance (in km). The metric starts with a base
Vincenty's Forumal distance calculation, then modifies this based on
whether the two points are in the same city and or city neighborhood.

This is just one (illustrative) method of using GADM features to modify
distance. It is "magic numbery" for simplicity. In real-life one would 
derive values for GADM feature weights -- or use the full proxy method.

##### `proxy` Mode
Custom distance metric that uses a simple proxy ID to fetch attributes
from an external data set (for illustrative simplicity in this case, 
the passed POI dataset)

>While this Proxy approach replicates the same distance formula
of _Vincenty-plus-GADM_ it could be modified to support **ANY** distance formula.
For example, rather that using GADM features one could instead extract 
a key or GUID used to look up a whole array of features used for a custom
distance calculation (even to make a REST call to a route planning system
to get true driving times between each X and Y). 

#### Specific CSV File Settings
The script can take in any CSV file of POIs, as long as the file contains
the requisite data points. A [sample](https://github.com/JimHaughwout/gadm_scan/blob/master/data/points_of_interest.csv) is provided
in the `/data` folder.

If you use your own file, simply set column names in the dictionary KEY values
in the [`settings.py`](https://github.com/JimHaughwout/gadm_scan/blob/master/settings.py) 
file as follows

Key | CSV Column name of | Nullable in CSV?
----|--------------------|---------
`LAT_KEY` | Latitude (in decimal degrees) | NO
`LNG_KEY` | Longitude (in decimal degrees) | NO
`ADDR_KEY` | Single-line Address (e.g., "77 Massachussetts Avenue, Cambridge, MA 02139") | Yes
`NBHD_KEY` | GADM Neighborhood Name| Yes for `vincenty-basic`
`CITY_KEY` | GADM City Name | Yes
`NAME_KEY` | POI Location Name | NO
`ZOA_KEY` | ZOA label you wish for output | N/A*

*Not part of `INPUT_FILE`. Used to create `OUTPUT_FILE`.

## Usage
`git clone` then update settings and run from the command line:
```sh
$ python dbscan_gadm_metric.py
```
