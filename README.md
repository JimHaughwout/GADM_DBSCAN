# gadm_scan
Fun with DBSCAN algorithm and GADM geocoded sites

The goal is to read in a set of coordinates (latitude and longitude), geocode [Global Administrative Area](http://www.gadm.org/) features
for these, then perform unsupervised learning to cluster these into zones of interest based on geographic features using the [Density-Based Spatial Clustering of Applications with Noise](https://en.wikipedia.org/wiki/DBSCAN) algorithm.
