import settings as s
import utils
import numpy as np
from sys import exit
from geopy.distance import vincenty


DEBUG = s.DEBUG


def get_name_list(poi_set):
    """
    Returns list of names of POIs in order of appearance in set
    """
    assert not isinstance(poi_set, basestring), 'POI set is not list or tuple'

    poi_names = list()
    for poi in poi_set:
        poi_names.append(poi[s.NAME_KEY])

    return(poi_names)


def get_centroid(poi_set):
    """
    Returns centroid lat,lng pair from list or tuple of POI dictionaries
    """
    lat_sum = 0.0
    lng_sum = 0.0

    assert not isinstance(poi_set, basestring), 'POI set is not list or tuple'
    poi_count = len(poi_set)
    assert poi_count > 0, 'Zero length POI set'

    for poi in poi_set:
        try:
            poi_lat = poi[s.LAT_KEY]
            poi_lng = poi[s.LNG_KEY]
        except:
            print "Get Centroid - Invalid POI: %s" % poi
            exit(10)

        lat_sum += poi_lat
        lng_sum += poi_lng

    c_lat = lat_sum / poi_count
    c_lng = lng_sum / poi_count

    return c_lat, c_lng


def poi_cart_projection(poi, centroid):
    """
    Projects a POI lat,lng as a cartesian projection relative to centroid 
    of all POIs
    """
    try:
        c_lat = centroid[0]
        c_lng = centroid[1]
    except:
        print "poi_cart_projection - Invalid Centroid: %s" % centroid
        exit(10)

    try:
        poi_lat = poi[s.LAT_KEY]
        poi_lng = poi[s.LNG_KEY]
    except:
        print "poi_cart_projection - Invalid POI: %s" % poi
        exit(11)

    x = vincenty((c_lat, c_lng), (c_lat, poi_lng)).km
    if c_lng > poi_lng: x *= -1.0

    y = vincenty((c_lat, c_lng), (poi_lat, c_lng)).km
    if c_lat > poi_lat: y *= -1.0

    """
    if DEBUG:
        print "\nPOI:\t\t%s" % poi[s.NAME_KEY]
        print "Coords:\t\t(%.4f, %.4f)" % (poi_lng, poi_lat)
        print "Centroid:\t(%.4f, %.4f)" % (c_lng, c_lat)
        print "Projects to:\t(%.4f, %4f)" % (x, y)
    """
    return (x, y)


def cart_projection(poi_set):
    """
    Projects set of POIs to X,Y Cartesian plan so DBSCAN can be used.
    We based this on the centroid of the POI set to minimize ellipsoid error
    """
    assert not isinstance(poi_set, basestring), 'POI set is not list or tuple'

    centroid = get_centroid(poi_set)
    poi_projected = list()

    for poi in poi_set:
        poi_projected.append(poi_cart_projection(poi, centroid))

    return poi_projected