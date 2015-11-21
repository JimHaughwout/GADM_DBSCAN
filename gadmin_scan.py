import settings as s
import utils
import xform
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.datasets.samples_generator import make_blobs
from sklearn.preprocessing import StandardScaler

DEBUG = s.DEBUG

##############################################################################
# Load in data
poi_set = utils.import_measures(s.DATA_FILE)



##############################################################################
# Project and Transform
labels_true = np.array(xform.get_name_list(poi_set))
projected_X = np.array(xform.cart_projection(poi_set))
X = StandardScaler().fit_transform(projected_X)

##############################################################################
# Compute DBSCAN
db = DBSCAN(eps=s.DEFAULT_RADIUS, min_samples=1).fit(X)
core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
core_samples_mask[db.core_sample_indices_] = True
labels = db.labels_

# Number of clusters in labels, ignoring noise if present.
n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

print('Estimated number of clusters: %d' % n_clusters_)
print("Homogeneity: %0.3f" % metrics.homogeneity_score(labels_true, labels))
print("Completeness: %0.3f" % metrics.completeness_score(labels_true, labels))
print("V-measure: %0.3f" % metrics.v_measure_score(labels_true, labels))
print("Adjusted Rand Index: %0.3f"
      % metrics.adjusted_rand_score(labels_true, labels))
print("Adjusted Mutual Information: %0.3f"
      % metrics.adjusted_mutual_info_score(labels_true, labels))
print("Silhouette Coefficient: %0.3f"
      % metrics.silhouette_score(X, labels))

##############################################################################
# Plot result
import matplotlib.pyplot as plt

# Black removed and is used for noise instead.
unique_labels = set(labels)
colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))
for k, col in zip(unique_labels, colors):
    if k == -1:
        # Black used for noise.
        col = 'k'

    class_member_mask = (labels == k)

    xy = X[class_member_mask & core_samples_mask]
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=col,
             markeredgecolor='k', markersize=14)

    xy = X[class_member_mask & ~core_samples_mask]
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=col,
             markeredgecolor='k', markersize=6)

plt.title('Estimated number of clusters: %d' % n_clusters_)
plt.show()








"""
if DEBUG:
    c_lat, c_lng = xform.get_centroid(poi_set)
    print "\nlabels_true is %s" % type(labels_true)
    print labels_true
    print "\nraw_X is %s" % type(raw_X)
    print raw_X
    print "\nCentroid is: (%.4f, %.4f)" % (c_lat, c_lng) 
    print "\nprojected_X is %s" % type(projected_X)
    print projected_X
    print "\nX is %s" % type(X)
    print X
"""
