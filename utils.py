import settings as s
import decimal
#import json
from csv import DictReader
from sys import exit
from geopy.distance import vincenty
from sklearn import metrics

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


def half_even(num_val, n_places=s.DEFAULT_ROUNDING):
    """
    ROUND_HALF_EVEN a point to n_places decimal places
    """
    if not 0 < n_places <= 8:
        print "Can only round to 1-8 decimal places. Rounding to default"
        n_places = s.DEFAULT_ROUNDING

    try:
        rounding = str(10**int(-1 * n_places))
        x = float(decimal.Decimal("%s" % num_val).quantize(decimal.Decimal(rounding), 
            rounding=decimal.ROUND_HALF_EVEN))
    except ValueError as e:
        e = "Could not round %r" % num_val
        print e
        raise
    return x

"""
def print_json(data):

    try:
        print json.dumps(data, indent=2, sort_keys=True)
    except ValueError as e:
        e = "Cannot convert data to JSON for printing:\n%r" % data
        print e
        raise e
"""

def import_measures(source_csv, lat_col=s.LAT_KEY, 
    lng_col=s.LNG_KEY, rounding=s.DEFAULT_ROUNDING):
    """"
    Reads in CSV, converting each row to a dictionary and attempting
    to half-even round lat and lng to rounding level.
    Appends to a list and returns the list for iterable in-memory processing

    TODO make this more generic on column names with a lambda function
    """
    measure_set = list()
    with open(source_csv) as csvfile:
        data = DictReader(csvfile)
        for row in data:
            try:
                row[lat_col] = half_even(row[lat_col], rounding)
                row[lng_col] = half_even(row[lng_col], rounding)
            except:
                print "No %s, %s entries in data file %s" % (lat_col, lng_col,
                 source_csv)
                exit(1)
            measure_set.append(row)

        if s.DEBUG:
            print "Imported %d POIs successfully from %s" % (len(measure_set),
             source_csv)

        return measure_set


def print_dbscan_metrics(X, n_clusters_, labels_true, labels):
    """
    Print metrics on DBSCAN to screen.
    """
    print "\nModel Performance and Metrics"
    print "="*80
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


def output_results(dbscan_labels, n_clusters_, poi_dataset, 
    screen=True, outfile=None):
    """
    Outputs results to screen or csv file
    """
    index_num = 0
    for zoa, poi in zip(dbscan_labels, poi_dataset):
        index_num += 1
        if screen:
            if index_num == 1:
                print "\nZOA Results: %d POIs in %d ZOAs" % (len(dbscan_labels), 
                    n_clusters_)
                print "="*80,
            print "\nLocation:\t%s" % poi[s.NAME_KEY]
            print "Address:\t%s" % poi[s.ADDR_KEY]
            print "Coords:\t\t(%.4f, %.4f)" % (poi[s.LAT_KEY], poi[s.LNG_KEY])
            print "ZOA ID:\t\t%d" % zoa 

        if outfile:
            # Validate outfile name
            assert isinstance (outfile, str), "Outfile name is not a string: %r" % name
            if outfile[-4:] != '.csv': outfile += '.csv'
            # Rest is TODO