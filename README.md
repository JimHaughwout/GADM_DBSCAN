# dbscan_gadm
Fun with DBSCAN algorithm and GADM-geocoded points of interest.

The goal is to read in a set of coordinates (latitude and longitude), 
geocode [Global Administrative Area](http://www.gadm.org/) features
for these, then perform unsupervised learning to cluster these into 
zones of interest based on geographic features using the 
[Density-Based Spatial Clustering of Applications with Noise](https://en.wikipedia.org/wiki/DBSCAN) algorithm.

## Versions
This repo currently includes two versions of the algorithm

#### DBSCAN With Conformal Mapping
This version uses a conformal mapping approach to map ellipsoid lat,lng 
coordinates on a Cartesian Plane. This allows use of sklearn's out-of-the-box 
distance calculation functions. It also produces try X-Y coordinates for
display via `matplotlib`

###### Usage
Create your own POI file or use the [sample](https://github.com/JimHaughwout/gadm_scan/blob/master/data/points_of_interest.csv) 
provided in the `/data` folder. Update [`settings.py`](https://github.com/JimHaughwout/gadm_scan/blob/master/settings.py) then:
```sh
$ python dbscan_conformal.py
```

#### DBSCAN With Vincenty Distance Metric
This version uses a custom distance metric function that employs true 
ellipsoid distance calculations (using Vincenty's formula). 

###### Usage
Create your own POI file or use the [sample](https://github.com/JimHaughwout/gadm_scan/blob/master/data/points_of_interest.csv) 
provided in the `/data` folder. Update [`settings.py`](https://github.com/JimHaughwout/gadm_scan/blob/master/settings.py) then:
```sh
$ python dbscan_gadm_metric.py
```

###### What's Next
The desire is to modify the metric calculation to employ GADM features to
change the distance calcultion (i.e., leverage urbanization vs rural features).

###### Known Issues
As (Lat, Lng) is actually (Y, X) `matplotlib` plots these with a 90-degree rotation.