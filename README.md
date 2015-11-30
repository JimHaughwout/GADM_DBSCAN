# dbscan_gadm
Fun with DBSCAN algorithm and GADM-geocoded points of interest.

This reads in a data set of coordinates (latitude and longitude) along with 
geocoded [Global Administrative Area](http://www.gadm.org/) features
for these, then performs unsupervised learning to cluster these into 
zones of interest based on geographic features using the 
[Density-Based Spatial Clustering of Applications with Noise](https://en.wikipedia.org/wiki/DBSCAN) 
algorithm with a customized distance function.

## Usage
Update options in [`settings.py`](https://github.com/JimHaughwout/gadm_scan/blob/master/settings.py) 
and run from the command line:
```sh
$ python dbscan_gadm_metric.py
```

## Custom Distance Metric Modes
You can use one of three modes to calculation the distance between points for
DBSCAN clustering

#### Vincenty Basic
Custom distance metric using [Vincenty's Formula](https://en.wikipedia.org/wiki/Vincenty%27s_formulae).

Set `MODE = 'vincenty-basic'` in `settings.py`.

#### Vincenty+GADM Features
Custom distance metric that combines Vincenty's Formula with GADM features
to calculate a scored distance (in km). The metric starts with a base
Vincenty's Forumal distance calculation, then modifies this based on
whether the two points are in the same city and or city neighborhood.

This is just one illustrative method of using GADM features to modify
distance. It is "magic numbery" for simplicity. In real-life one would 
derive values for GADM feature weights -- or use the full proxy method.

Set `MODE = 'vincenty-gadm'` in `settings.py`.

#### Proxy Distance Calculation
Custom distance metric that uses a simple proxy ID to fetch attributes
from an external data set (for illustrative simplicity in this case, 
we use the passed POI dataset)

>While this Proxy approach replicates the same distance formula
of _Vincenty-plus-GADM_ it could be modified to support **ANY** distance formula.
For example, rather that using GADM features one could instead extract 
a key or GUID used to look up a whole array of features used for a custom
distance calculation (even to make a REST call to a route management system
to get true driving times between each X and Y). 

Set `MODE = 'proxy'` in `settings.py`.

#### Sample Results
A [sample data file](https://github.com/JimHaughwout/GADM_DBSCAN/blob/master/sample-data/points_of_interest.csv) of 10 points of interest is provided in the [/sample-data](https://github.com/JimHaughwout/GADM_DBSCAN/tree/master/sample-data) folder to illustrate the results of different DBSCAN distance calculations. These points were selected to show different clustering results based on whether or not GADM features are used.

Here is a map of all 10 points:
![All Points](https://github.com/JimHaughwout/GADM_DBSCAN/blob/master/sample-results/map_all.png)

##### Vincenty Basic
When looking at the 10 points from a simple human "how would you cluster these?" perspective, it appears we have five clusters.
This is exactly how the the *Vincenty Basic* distance formula clusters these (when set to allow clusters of 1+ points and to treat anything within a 1.0 km radius as candidates in the same cluster: 

```
Model Performance and Metrics
================================================================================
Estimated number of clusters: 5
Homogeneity: 0.676
Completeness: 1.000
V-measure: 0.807
Adjusted Rand Index: 0.000
Adjusted Mutual Information: 0.000
Silhouette Coefficient: 0.930
```
You can see the raw results [here](https://github.com/JimHaughwout/GADM_DBSCAN/blob/master/sample-results/vincenty-basic_results.txt). A `matplotlib` view shows a Mercator projection of five separate clusters:
![V-basic](https://github.com/JimHaughwout/GADM_DBSCAN/blob/master/sample-results/vicenty-basic.png)

This appears to "make sense" from a common common sense POV.

##### Adding GADM Features
However, lets see what happens if we use Vincenty distance modified by GADM features to determine clusters. In this case we have
applied two rules based on a very simplistic urban model:

1. Urban travel is harder than non-urban. If two points are in the same city, and the city is large enought to have distinct GADM neighborhoods (a.k.a. localities), then provide a 100% distance penality.
2. However, assume that intercity neighborhoods are defined based on natural human clusters. As such, if two points are in the same city AND are in the same neighborhood locality, then give a 20% distance bonus.

Applying these rules yields 7 clusters (vs. 5):
```
Model Performance and Metrics
================================================================================
Estimated number of clusters: 7
Homogeneity: 0.819
Completeness: 1.000
V-measure: 0.901
Adjusted Rand Index: 0.000
Adjusted Mutual Information: 0.000
Silhouette Coefficient: 0.467
```
You can see the raw results [here](https://github.com/JimHaughwout/GADM_DBSCAN/blob/master/sample-results/vincenty-plus-gadm_results.txt). Here is the `matplotlib` Mercator view:
![V-GADM](https://github.com/JimHaughwout/GADM_DBSCAN/blob/master/sample-results/vincenty-plus-gadm_matplotlib.png)

This view shows two places where simple Vincenty clusters were divided: Arlington, VA and central Washington, DC:

###### Let's look at Arlington
The two POIs in Arlington are within 1 km of each other but in two different neighborhoods (*Virginia Square* and *Waverly Hills*). These neighborhoods are separated by Route I-66:
![Arlington](https://github.com/JimHaughwout/GADM_DBSCAN/blob/master/sample-results/map_arlington.png)
Adding the modified GADM rule allowd DBSCAN to "recognize" this using neighborhood as a human proxy input.

###### Let's look at Washington, DC
Adding GADM features split the three Washington POIs into two clusters (even though all were within 1 km of each other). One cluster was to the west of *The White House* (in *Northwest Washington*). The other was north (in *Downtown*):
![DC Neighborhood](https://github.com/JimHaughwout/GADM_DBSCAN/blob/master/sample-results/map_dc.png)
Anyone who has driven around DC will tell you this makes sense also, as the *The White House* creates lots of detours.

###### Intra-neighborhood Traffic
As expected, using GADM features kept points that are close together AND in the same intercity neighborhood together. Here is Old Town, Alexandria:
![By the Pad](https://github.com/JimHaughwout/GADM_DBSCAN/blob/master/sample-results/map_old_town.png)

## Options
Currently the program defines options in a [`settings.py`](https://github.com/JimHaughwout/gadm_scan/blob/master/settings.py) file:

#### Program Settings
Setting | Description | Example Values
----------------|-------------|-------
`INPUT_FILE` | Source data file of coordinates | See below
`OUTPUT_FILE` | Output data file name | Qualified filename with path
`ZOA_SUMMARY_TO_SCREEN` | Print ZOA summary to screen | `True`, `False`
`MATPLOT_ZOA_CLUSTERS` | Use `matplotlib` to graph clusters | `True`, `False`
`MODE` | Custom distance metric formula to use. See below. | See above
`DEFAULT_RADIUS` | Default ZOA radius for DBSCAN epsilon, in km | `1.0`
`DEFAULT_ROUNDING` | Default rounding in decimal places, for GPS coordinates. | `4`
`LOCAL`* | Adjustment factor for coordinates in same  neighborhood | `0.8`
`X_TOWN`* | Adjustment factor for coordinates in same city | `2.0`

*These are settings are ignored in `vincenty-basic` mode. See _Sample Results_ above for discussion of use of `LOCAL` and `X_TOWN` settings.

#### CSV File Settings
The script can take in any CSV file of POIs, as long as the file contains
the requisite data points. A [sample](https://github.com/JimHaughwout/gadm_scan/blob/master/sample-data/points_of_interest.csv) is provided
in the `/sample-data` folder.

If you use your own file, simply set column names in the dictionary KEY values
in the [`settings.py`](https://github.com/JimHaughwout/gadm_scan/blob/master/settings.py) 
file as follows

Key | CSV Column name of | Null Allowed in CSV?
----|--------------------|---------
`LAT_KEY` | Latitude (in decimal degrees) | NO
`LNG_KEY` | Longitude (in decimal degrees) | NO
`ADDR_KEY` | Single-line Address (e.g., "77 Massachussetts Avenue, Cambridge, MA 02139") | Yes
`NBHD_KEY` | GADM Neighborhood Name| Yes for `vincenty-basic`
`CITY_KEY` | GADM City Name | Yes
`NAME_KEY` | POI Location Name | NO
`ZOA_KEY`* | ZOA label you wish for output | N/A

*Not part of `INPUT_FILE`. Used to create `OUTPUT_FILE`.
