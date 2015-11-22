import settings as s
import utils
import numpy as np
from sys import exit
from geopy.distance import vincenty


DEBUG = s.DEBUG


def build_gadm_X(poi_dataset):
    """
    TODO
    """
    assert not isinstance(poi_dataset, basestring), 'POI dataset is not list or tuple'

    X_list = list()

    for poi in poi_dataset:
        try:
            lat = poi[s.LAT_KEY]
            lng = poi[s.LNG_KEY]
            city = poi[s.CITY_KEY]
            nbhd = poi[s.NBHD_KEY]
        except:
            print "\nget_poi_coord_dataset - Invalid POI: %r" % poi
            exit(20)
        
        X_list.append((lat, lng, city, nbhd))

    return poi_coords


def get_poi_coord_dataset(poi_dataset):
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


def geodist(p1, p2):
    """
    TODO
    """
    distance_km = vincenty(p1, p2).km

    #if DEBUG: print "Distance %s - %s: %.4f km" % (p1, p2, distance_km)

    return distance_km


def dist_calc(poi_1, poi_2, mode='simple'):
    """
    TODO DOCS
    """
    # Ensure we actually have dicts with values needed
    try:
        point_1 = (poi_1[s.LAT_KEY], poi_1[s.LNG_KEY])
        name_1 = poi_1[s.NAME_KEY]
        nbhd_1 = poi_1[s.NBHD_KEY]
        city_1 = poi_1[s.CITY_KEY]
        point_2 = (poi_2[s.LAT_KEY], poi_2[s.LNG_KEY])
        name_2 = poi_2[s.NAME_KEY]
        nbhd_2 = poi_2[s.NBHD_KEY]
        city_2 = poi_2[s.CITY_KEY]
    except:
        print "\nPassed invalid POIs"
        print "POI 1:\n%r" % poi_1
        print "POI 2:\n%r\n" % poi_2
        exit(3)

    # Magic Numbery rules are to test was to use GADM features for distance
    # For now we treat close points in a city as a penalty (due to traffic)
    # But treat close points in the same Neighborhood as a bonus
    # This gives us simple urbanization
    # TODO real data science scalars or use open data like this 
    # http://infinitemonkeycorps.net/projects/cityspeed/
    multiplier = 1.0
    if mode == 'gadm':
        if city_1 == city_2:
            multiplier *= 4.0
        if nbhd_1 == nbhd_2:
            multiplier *= 0.8

    distance = vincenty(point_1, point_2).km
    
    if s.DEBUG:
        print "%s-%s\nDistance (km): %.3f\nMultiplier: %.2f\n" % (name_1, 
            name_2, distance, multiplier)

    return distance * multiplier