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
    X_len = len(X)
    assert X_len >= 1, 'lat_lng_tpose - Passed zero length X %r' % X

    lngs = X[:,1] # X values
    lats = X[:,0] # Y values
    x = np.reshape(lngs, (X_len, 1))
    y = np.reshape(lats, (X_len, 1))

    X_prime = np.hstack((x, y))

    return X_prime


def lat_lng_tpose2(X, poi_dataset):
    """
    TODO
    """
    assert len(X) >= 1, 'lat_lng_tpose2 - Passed zero length X %r' % X
    assert not isinstance(poi_dataset, basestring), 'POI dataset is not list or tuple'

    coordinates = list()
    for item in X:
        try:
            poi_id = int(item[0])
            poi = poi_dataset[poi_id]
            x = poi[s.LNG_KEY]
            y = poi[s.LAT_KEY]
        except:
            print "TODO %r" % item
            exit(60)
        coordinates.append((x, y))

    X_prime = np.array(coordinates)
    if DEBUG: print X_prime
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


def get_proxy_X(poi_dataset):
    """TODO branch proxy """
    assert not isinstance(poi_dataset, basestring), 'POI dataset is not list or tuple'

    poi_ids = list()

    poi_id = 0
    for poi in poi_dataset:
        try:
            # Verify poi_dataset has data we need - TODO abstract this
            poi_lat = poi[s.LAT_KEY]
            poi_lng = poi[s.LNG_KEY]
            poi_city = poi[s.CITY_KEY]
            poi_neighborhood = poi[s.NBHD_KEY]
        except:
            print "\nget_proxy_X - Invalid POI: %r" % poi
            exit(20)
        
        poi_ids.append((poi_id, poi_id))
        poi_id += 1

    return poi_ids

 
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


def extract_features_from_proxy(x, poi_dataset):
    """
    x is a slice of the X numpy array
    """
    assert not isinstance(poi_dataset, basestring), 'POI dataset is not list or tuple'

    #print poi_id

    try:
        poi_id = int(x[0])
        poi = poi_dataset[poi_id]
        lat = poi[s.LAT_KEY]
        lng = poi[s.LNG_KEY]
        city = poi[s.CITY_KEY]
        neighborhood = poi[s.NBHD_KEY]
    except:
        print "extract_features: %r is not a valid POI dictionary" % poi
        exit(41)

    return poi_id, (lat, lng), city, neighborhood


def geodist_proxy(x, y, poi_dataset):
    """TODO documentation"""
    try:
        poi_id1, p1, c1, n1 = extract_features_from_proxy(x, poi_dataset)
    except:
        print "geodist_proxy - x is not valid: %r" % x
        exit(51)

    try:
        poi_id2, p2, c2, n2 = extract_features_from_proxy(y, poi_dataset)
    except:
        print "geodist_proxy - y is not valid: %r" % y
        exit(52)

    base_distance = vincenty(p1, p2).km
    scored_distance = base_distance

    if c1 == c2: scored_distance *= s.X_TOWN
    if n1 == n2: scored_distance *= s.LOCAL

    if DEBUG and poi_id1 != poi_id2: 
        print "Distance %s (%s, %s) - %s (%s, %s): %.4f km (as %.4f)" % (p1, n1,
         c1, p2, n2, c2, base_distance, scored_distance)

    return scored_distance


def geodist_gadm(x, y, poi_dataset):
    """TODO documentation"""
    try:
        p1, idx1 = extract_features(x) # (lat,lng) & index in poi_dataset
        n1 = poi_dataset[idx1][s.NBHD_KEY] # neighborhood based on index
        c1 = poi_dataset[idx1][s.CITY_KEY] # neighborhood based on index
    except:
        print "geodist_gadm - x is not valid: %r" % x

    try:
        p2, idx2 = extract_features(y) # (lat,lng) & index in poi_dataset
        n2 = poi_dataset[idx2][s.NBHD_KEY] # neighborhood based on index
        c2 = poi_dataset[idx2][s.CITY_KEY] # neighborhood based on index
    except:
        print "geodist_gadm - y is not valid: %r" % y

    base_distance = vincenty(p1, p2).km
    scored_distance = base_distance

    if c1 == c2: scored_distance *= s.X_TOWN
    if n1 == n2: scored_distance *= s.LOCAL

    if DEBUG and idx1 != idx2: 
        print "Distance %s (%s, %s) - %s (%s, %s): %.4f km (as %.4f)" % (p1, n1,
         c1, p2, n2, c2, base_distance, scored_distance)

    return scored_distance