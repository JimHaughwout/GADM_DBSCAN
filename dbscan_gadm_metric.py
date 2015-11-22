import settings as s
import utils
import gadm
#import xform # For now
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt


DEBUG = s.DEBUG

"""
Uses DBSCAN to extract clusters (called Zones of Analysis) 
from a set of geocoded Point of Interest locations (read in from a CSV file).

This version uses a custom distance metric function that employs true 
ellipsoid distance calculations (using Vincenty's formula). 

TODO - PEP8-style documentation.
"""

##############################################################################
# Load in data
poi_dataset = utils.import_poi_csv(s.INPUT_FILE)

##############################################################################
# Project and Transform
labels_true = np.array(utils.get_name_list(poi_dataset))
X = np.array(gadm.get_poi_coord_dataset(poi_dataset))

##############################################################################
# Compute DBSCAN

db = DBSCAN(eps=s.DEFAULT_RADIUS, min_samples=1,metric=lambda X, Y: gadm.geodist(X, Y)).fit(X)
#db = DBSCAN(eps=s.DEFAULT_RADIUS, min_samples=1).fit(X)
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
utils.output_results(poi_result_set, screen=True, outfile=s.OUTPUT_FILE)

##############################################################################
# Plot result
# As Lat,Lng is Y,X we need to transpose it
X_prime = gadm.lat_lng_tpose(X)

# Black removed and is used for noise instead.
unique_labels = set(labels)
colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))

fig = plt.figure()
ax = fig.add_subplot(111)

for k, col in zip(unique_labels, colors):
    if k == -1:
        # Black used for noise.
        col = 'k'

    class_member_mask = (labels == k)

    xy = X_prime[class_member_mask & core_samples_mask]
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=col,
             markeredgecolor='k', markersize=14)

    xy = X_prime[class_member_mask & ~core_samples_mask]
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=col,
             markeredgecolor='k', markersize=6)

plt.title('Estimated number of clusters: %d' % n_clusters_)
plt.show()