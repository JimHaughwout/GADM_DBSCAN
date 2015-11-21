# gadm_scan
Fun with DBSCAN algorithm and GADM geocoded sites

The goal is to read in a set of coordinates (latitude and longitude), geocode [Global Administrative Area](http://www.gadm.org/) features
for these, then cluster these into zones of interest based on geographic features using [DBSCAN](https://en.wikipedia.org/wiki/DBSCAN).
