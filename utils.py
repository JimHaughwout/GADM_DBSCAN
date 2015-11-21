import settings
import json
import decimal
from sys import exit
import csv
from geopy.distance import vincenty

def dist_calc(poi_1, poi_2, mode='simple'):
    """
    TODO DOCS
    """
    # Ensure we actually have dicts with values needed
    try:
        point_1 = (poi_1[settings.LAT_KEY], poi_1[settings.LNG_KEY])
        name_1 = poi_1[settings.NAME_KEY]
        nbhd_1 = poi_1[settings.NBHD_KEY]
        city_1 = poi_1[settings.CITY_KEY]
        point_2 = (poi_2[settings.LAT_KEY], poi_2[settings.LNG_KEY])
        name_2 = poi_2[settings.NAME_KEY]
        nbhd_2 = poi_2[settings.NBHD_KEY]
        city_2 = poi_2[settings.CITY_KEY]
    except:
        print "\nPassed invalid POIs"
        print "POI 1:\n%r" % poi_1
        print "POI 2:\n%r\n" % poi_2
        exit(3)

    # Magic Numbery rules are to test was to use GADM features for distance
    # For now we treat close points in a city as a penalty (due to traffic)
    # But treat close points in the same Neighborhood as a bonus
    # This gives us simple urbanization
    # TODO real data science scalars
    multiplier = 1.0
    if mode == 'gadm':
        if city_1 == city_2:
            multiplier *= 2.0
        if nbhd_1 == nbhd_2:
            multiplier *= 0.4

    distance = vincenty(point_1, point_2).km
    
    if settings.DEBUG:
        print "%s-%s\nDistance (km): %.3f\nMultiplier: %.2f\n" % (name_1, name_2, distance, multiplier)

    return distance * multiplier


def half_even(num_val, n_places=settings.DEFAULT_ROUNDING):
    """
    ROUND_HALF_EVEN a point to n_places decimal places
    """
    if not 0 < n_places <= 8:
        print "Can only round to 1-8 decimal places. Rounding to default"
        n_places = settings.DEFAULT_ROUNDING

    try:
        rounding = str(10**int(-1 * n_places))
        x = float(decimal.Decimal("%s" % num_val).quantize(decimal.Decimal(rounding), 
            rounding=decimal.ROUND_HALF_EVEN))
    except ValueError as e:
        e = "Could not round %r" % num_val
        print e
        raise
    return x


def print_json(data):
    """
    Prints out algorthm data in human-readable JSON
    """
    try:
        print json.dumps(data, indent=2, sort_keys=True)
    except ValueError as e:
        e = "Cannot convert data to JSON for printing:\n%r" % data
        print e
        raise e


def import_measures(source_csv, lat_col=settings.LAT_KEY, 
    lng_col=settings.LNG_KEY, rounding=settings.DEFAULT_ROUNDING):
    """"
    Reads in CSV, converting each row to a dictionary and attempting
    to half-even round lat and lng to rounding level.
    Appends to a list and returns the list for iterable in-memory processing

    TODO make this more generic on column names with a lambda function
    """
    measure_set = list()
    with open(source_csv) as csvfile:
        data = csv.DictReader(csvfile)
        for row in data:
            try:
                row[lat_col] = half_even(row[lat_col], rounding)
                row[lng_col] = half_even(row[lng_col], rounding)
            except:
                print "No %s, %s entries in data file %s" % (lat_col, lng_col, source_csv)
                exit(1)
            measure_set.append(row)

        if settings.DEBUG:
            print "Imported %d points of interest successfully from %s" % (len(measure_set), source_csv)

        return measure_set