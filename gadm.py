import settings as s
import utils
import numpy as np
from sys import exit
from geopy.distance import vincenty


DEBUG = s.DEBUG

def lat_lng_tpose(X):
    """
    Takes numpy array in [[Lat Lng]] format and returns in [[Lng Lat]] format
    so we can plot correctly as [[X, Y]] values
    """
    s = len(X)
    assert s >= 1, 'lat_lng_tpose - Passed zero length XL %r' % X

    lngs = X[:,1] # X values
    lats = X[:,0] # Y values
    x = np.reshape(lngs, (s, 1))
    y = np.reshape(lats, (s, 1))

    X_prime = np.hstack((x, y))

    return X_prime


def get_poi_coord(poi_dataset):
    """
    Extracts list of lat,lng coordinates from list of POI dictionaries
    """
    assert not isinstance(poi_dataset, basestring), 'POI dataset is not list or tuple'

    poi_coords = list()

    for poi in poi_dataset:
        try:
            poi_lat = poi[s.LAT_KEY]
            poi_lng = poi[s.LNG_KEY]
        except:
            print "\nget_poi_coord_dataset - Invalid POI: %r" % poi
            exit(20)
        
        poi_coords.append((poi_lat, poi_lng))

    return poi_coords


def get_poi_coord_with_idx(poi_dataset):
    """
    Extracts coord set and appends rest 
    """
    assert not isinstance(poi_dataset, basestring), 'POI dataset is not list or tuple'

    poi_coords = list()

    idx = 0
    for poi in poi_dataset:
        try:
            poi_lat = poi[s.LAT_KEY]
            poi_lng = poi[s.LNG_KEY]
        except:
            print "\nget_poi_coord_dataset - Invalid POI: %r" % poi
            exit(20)
        
        poi_coords.append((poi_lat, poi_lng, idx))
        idx += 1

    return poi_coords

 
def geodist_v(p1, p2):
    """TODO documentation"""
    print "%s - %s" % (p1, p2)

    base_distance = vincenty(p1, p2).km

    if DEBUG: print "Distance %s - %s: %.4f km" % (p1, p2, distance_km)

    return base_distance


def extract_features(x):
    """
    x is a slice of the X numpy array
    """
    try:
        lat = utils.half_even(x[0], s.DEFAULT_ROUNDING)
        lng = utils.half_even(x[1], s.DEFAULT_ROUNDING)
        idx = int(x[2])
    except:
        print "extract_features: %r is not valid" % x
        exit(40)

    return (lat, lng), idx


def geodist_gadm(x, y, poi_dataset):
    """TODO documentation"""
    try:
        p1, idx1 = extract_features(x) # (lat,lng) & index in poi_dataset
        n1 = poi_dataset[idx1][s.NBHD_KEY] # neighborhood based on index
        c1 = poi_dataset[idx1][s.CITY_KEY] # neighborhood based on index
    except:
        print "geodist2 - x is not valid: %r" % x

    try:
        p2, idx2 = extract_features(y) # (lat,lng) & index in poi_dataset
        n2 = poi_dataset[idx2][s.NBHD_KEY] # neighborhood based on index
        c2 = poi_dataset[idx2][s.CITY_KEY] # neighborhood based on index
    except:
        print "geodist2 - y is not valid: %r" % x

    base_distance = vincenty(p1, p2).km
    scored_distance = base_distance

    if c1 == c2: scored_distance *= s.X_TOWN
    if n1 == n2: scored_distance *= s.LOCAL

    if DEBUG and idx1 != idx2: 
        print "Distance %s (%s, %s) - %s (%s, %s): %.4f km (as %.4f)" % (p1, n1,
         c1, p2, n2, c2, base_distance, scored_distance)

    return scored_distance