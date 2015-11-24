import settings as s
import utils
import gadm
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN

from sys import exit # For now

DEBUG = s.DEBUG

"""
This reads in a data set of coordinates (latitude and longitude) along with 
geocoded features for these, then performs unsupervised learning to cluster 
these into zones of affinity based on geographic features using the 
Density-Based Spatial Clustering of Applications with Noise algorithm
with a customized distance function. 

TODO - PEP8-style documentation.
"""

##############################################################################
# Load in data
poi_dataset = utils.import_poi_csv(s.INPUT_FILE)

##############################################################################
# Transform and Compute DBSCAN
labels_true = np.array(utils.get_name_list(poi_dataset))

if s.GADM_MODE:
    X = np.array(gadm.get_poi_coord_with_idx(poi_dataset))
    db = DBSCAN(eps=s.DEFAULT_RADIUS, min_samples=1,metric=lambda X, Y: gadm.geodist_gadm(X, Y, poi_dataset)).fit(X)
else:
    X = np.array(gadm.get_poi_coord(poi_dataset))
    db = DBSCAN(eps=s.DEFAULT_RADIUS, min_samples=1,metric=lambda X, Y: gadm.geodist_v(X, Y)).fit(X)

core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
core_samples_mask[db.core_sample_indices_] = True
labels = db.labels_

# Number of clusters in labels, ignoring noise if present.
n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

##############################################################################
# Print machine learning metrics
utils.print_dbscan_metrics(X, n_clusters_, labels_true, labels)

##############################################################################
# TODO - Xform Back, compute zone size and centroid
poi_result_set = utils.add_zoas_to_poi_dataset(labels, poi_dataset)

##############################################################################
# Output Results
utils.output_results(poi_result_set,
 screen=s.ZOA_SUMMARY_TO_SCREEN, outfile=s.OUTPUT_FILE)

##############################################################################
# Plot result
if s.MATPLOT_ZOA_CLUSTERS:
    X_prime = gadm.lat_lng_tpose(X) # As Lat,Lng is Y,X we need to transpose it
    utils.plot_results(labels, X_prime, core_samples_mask)