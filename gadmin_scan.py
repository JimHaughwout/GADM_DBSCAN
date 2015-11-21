import settings as s
import utils
import xform
import numpy as np
from sklearn.preprocessing import StandardScaler

DEBUG = s.DEBUG

poi_set = utils.import_measures(s.DATA_FILE)

# Create labels
poi_names = list()
poi_coords = list()
for poi in poi_set:
    poi_names.append(poi[s.NAME_KEY])
    poi_coords.append((poi[s.LAT_KEY], poi[s.LNG_KEY]))


labels_true = np.array(poi_names)
raw_X = np.array(poi_coords)
projected_X = np.array(xform.cart_projection(poi_set))
X = StandardScaler().fit_transform(projected_X)

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

