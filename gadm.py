import settings as s
import utils
import numpy as np
from sys import exit
from geopy.distance import vincenty

DEBUG = s.DEBUG

def get_vincenty_basic_X(poi_dataset):
    """
    Extracts list of lat,lng coordinates from list of POI dictionaries.
    Used for the Basic Vincenty Distance case
    """
    assert not isinstance(poi_dataset, basestring), 'POI dataset is not list or tuple'

    poi_coords = list()

    for poi in poi_dataset:
        try:
            poi_lat = poi[s.LAT_KEY]
            poi_lng = poi[s.LNG_KEY]
        except:
            print "\nget_poi_coord_dataset - Invalid POI: %r" % poi
            exit(10)
        
        poi_coords.append((poi_lat, poi_lng))

    return np.array(poi_coords)


def get_vincenty_gadm_X(poi_dataset):
    """
    Extracts list of lat,lng coordinates from list of POI dictionaries
    then appends the index that points the dictionary of the POI used to
    derive these. This allows the Vincenty+GADM use case to extract the added
    GADM features from a passed poi_dataset
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

    return np.array(poi_coords)


def get_proxy_X(poi_dataset):
    """
    Extracts proxy index points to each dictionary from a list of POI
    dictionaries. Use for Proxy use case

    While this Proxy approach replicates the same distance formula
    of Vincenty+GADM is could be modified to support ANY distance formula.
    For example, rather that using GADM features one could instead extract 
    a key or GUID used to look up a whole array of features used for a custom
    distance calculation (even to make a REST call to a route planning system
    to get true driving times between each X and Y). 

    NOTE: DBSCAN requires a numpy array of floats (all values in a numpy array
    must be of the same datatype) that has a minimum of two columns (even if
    one is using a lambda function). As a hack around this limitation we store
    the index in the dataset in each column. We have to cast back as a in int 
    as DBSCAN requires float. This allows us to use DBSCAN without modification.

    """
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
            exit(30)
        
        poi_ids.append((poi_id, poi_id))
        poi_id += 1

    return np.array(poi_ids)

 
def geodist_v(p1, p2):
    """
    Custom distance metric using Vincenty's Forumla. Returns results in km.
    """
    distance = vincenty(p1, p2).km

    if DEBUG: print "Distance %s - %s: %.4f km" % (p1, p2, distance)

    return distance


def extract_features(x):
    """
    Helper function to extract features for Vincenty+GADM distance metric.
    x is a slice of the X numpy array
    """
    try:
        lat = utils.half_even(x[0], s.DEFAULT_ROUNDING)
        lng = utils.half_even(x[1], s.DEFAULT_ROUNDING)
        idx = int(x[2])
    except:
        print "extract_features: %r is not valid" % x
        exit(21)

    return (lat, lng), idx


def geodist_gadm(x, y, poi_dataset):
    """
    Custom distance metric that combines Vincenty's Forumla with GADM features
    to calculate a scored distance (in km). The metric starts with a base
    Vincenty's Forumal distance calculation, then modifies this based on
    whether the two points are in the same city and or city neighborhood.

    This is just one (illustrative) method of using GADM features to modify
    distance. It is "magic numbery" for simplicity. In real-life one would 
    derive values for GADM feature weights -- or use the full proxy method.
    """
    try:
        p1, idx1 = extract_features(x) # (lat,lng) & index in poi_dataset
        n1 = poi_dataset[idx1][s.NBHD_KEY] # neighborhood based on index
        c1 = poi_dataset[idx1][s.CITY_KEY] # neighborhood based on index
    except:
        print "geodist_gadm - x is not valid: %r" % x
        exit(22)

    try:
        p2, idx2 = extract_features(y) # (lat,lng) & index in poi_dataset
        n2 = poi_dataset[idx2][s.NBHD_KEY] # neighborhood based on index
        c2 = poi_dataset[idx2][s.CITY_KEY] # neighborhood based on index
    except:
        print "geodist_gadm - y is not valid: %r" % y
        exit(23)

    base_distance = vincenty(p1, p2).km
    scored_distance = base_distance

    # If traveling within same city that is big enough to have neighborhoods
    if c1 == c2 and (n1 != None or n2 != None):
        if n1 == n2: scored_distance *= s.LOCAL # In-neighborhood bonus
        else: scored_distance *= s.X_TOWN # Cross-town penalty

    if DEBUG and idx1 != idx2: 
        print "Distance %s (%s, %s) - %s (%s, %s): %.4f km (as %.4f)" % (p1, n1,
         c1, p2, n2, c2, base_distance, scored_distance)

    return scored_distance


def extract_features_from_proxy(x, poi_dataset):
    """
    Helper function to extract features used for proxy distance metric.
    x is a slice of the X numpy array
    """
    assert not isinstance(poi_dataset, basestring), 'POI dataset is not list or tuple'

    try:
        poi_id = int(x[0])
        poi = poi_dataset[poi_id]
        lat = poi[s.LAT_KEY]
        lng = poi[s.LNG_KEY]
        city = poi[s.CITY_KEY]
        neighborhood = poi[s.NBHD_KEY]
    except:
        print "extract_features: %r is not a valid POI dictionary" % poi
        exit(31)

    return poi_id, (lat, lng), city, neighborhood


def geodist_proxy(x, y, poi_dataset):
    """
    Custom distance metric that uses a simple proxy ID to fetch attributes
    from an external data set (for illustrative simplicity in this case, 
    the passed POI dataset)

    While this Proxy approach replicates the same distance formula
    of Vincenty-plus-GADM it could be modified to support ANY distance formula.
    For example, rather that using GADM features one could instead extract 
    a key or GUID used to look up a whole array of features used for a custom
    distance calculation (even to make a REST call to a route planning system
    to get true driving times between each X and Y). 

    NOTE: DBSCAN requires a numpy array of floats (all values in a numpy array
    must be of the same datatype) that has a minimum of two columns (even if
    one is using a lambda function). As a hack around this limitation we store
    the index in the dataset in each column. We have to cast back as a in int 
    as DBSCAN requires float. This allows us to use DBSCAN without modification.
    """
    try:
        poi_id1, p1, c1, n1 = extract_features_from_proxy(x, poi_dataset)
    except:
        print "geodist_proxy - x is not valid: %r" % x
        exit(32)

    try:
        poi_id2, p2, c2, n2 = extract_features_from_proxy(y, poi_dataset)
    except:
        print "geodist_proxy - y is not valid: %r" % y
        exit(33)

    base_distance = vincenty(p1, p2).km
    scored_distance = base_distance

    if c1 == c2 and (n1 != None and n2 != None): # See note above
        if n1 == n2: scored_distance *= s.LOCAL
        else: scored_distance *= s.X_TOWN

    if DEBUG and poi_id1 != poi_id2: 
        print "Distance %s (%s, %s) - %s (%s, %s): %.4f km (as %.4f)" % (p1, n1,
         c1, p2, n2, c2, base_distance, scored_distance)

    return scored_distance


def lat_lng_tpose(X):
    """
    Takes DBSCAN X numpy array in [[Lat Lng]] format and returns a numppy array 
    in [[Lng Lat]] format so we can plot correctly as [[X, Y]] values
    """
    X_len = len(X)
    assert X_len >= 1, 'lat_lng_tpose - Passed zero length X %r' % X

    # Column 0 of X array is latitudes (Y values), Column 1 is is longitudes (X)
    try:
        lngs = X[:,1] 
        lats = X[:,0] 
        x = np.reshape(lngs, (X_len, 1))
        y = np.reshape(lats, (X_len, 1))
    except:
        print "X is invalid format: %r" % X
        exit(40)

    X_prime = np.hstack((x, y))

    return X_prime


def lat_lng_tpose_from_proxy(X, poi_dataset):
    """
    Takes in a DBSCAN numpy array of "proxy" indices  (i.e., no lat, long pairs:
    just and index the POI in the data set list) along with the poi dataset. 
    Uses this information to extract an X_prime numpy array of [[X, Y]] values
    that can be plotted in matplotlib

    NOTE: DBSCAN requires a numpy array of floats (all values in a numpy array
    must be of the same datatype) that has a minimum of two columns (even if
    one is using a lambda function). As a hack around this limitation we store
    the index in the dataset in each column. We have to cast back as a in int 
    as DBSCAN requires float.
    """
    assert len(X) >= 1, 'lat_lng_tpose_from_proxy - Passed zero length X %r' % X
    assert not isinstance(poi_dataset, basestring), 'POI dataset is not list or tuple'

    coordinates = list()
    for item in X:
        try:
            poi_id = int(item[0])
            poi = poi_dataset[poi_id]
            x = poi[s.LNG_KEY]
            y = poi[s.LAT_KEY]
        except:
            print "lat_lng_tpose_from_proxy - %r is not a valid POI" % item
            exit(41)
        coordinates.append((x, y))

    X_prime = np.array(coordinates)
    if DEBUG: print X_prime
    return X_prime