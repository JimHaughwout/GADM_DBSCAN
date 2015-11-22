import settings as s
import decimal
from csv import DictReader, DictWriter, writer
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


def import_poi_csv(source_csv, lat_col=s.LAT_KEY, 
    lng_col=s.LNG_KEY, rounding=s.DEFAULT_ROUNDING):
    """"
    Reads in CSV, converting each row to a POI dictionary and attempting
    to half-even round lat and lng to rounding level.
    Appends to a list and returns the list for iterable in-memory processing

    TODO make this more generic on column names with a lambda function
    """
    if str(source_csv)[-4:] != '.csv':
        print "import_poi_csv: %s is not a csv file" % source_csv
        exit(1)

    poi_dataset = list()
    poi_count = 0
    with open(source_csv) as source:
        data = DictReader(source)
        for row in data:
            try:
                row[lat_col] = half_even(row[lat_col], rounding)
                row[lng_col] = half_even(row[lng_col], rounding)
            except:
                print "No %s, %s entries in data file %s" % (lat_col, lng_col,
                 source_csv)
                exit(1)
            poi_dataset.append(row)
            poi_count += 1

        if s.DEBUG:
            print "Imported %d POIs successfully from %s" % (poi_count, source_csv)

        return poi_dataset


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


def add_zoas_to_poi_dataset(dbscan_labels, poi_dataset):
    """
    Modifies a list of POI dictionaries to add ZOAs from DBSCAN
    """
    poi_dataset_with_zoas = list()
    for zoa, poi in zip(dbscan_labels, poi_dataset):
        poi[s.ZOA_KEY] = zoa
        poi_dataset_with_zoas.append(poi)

    return poi_dataset_with_zoas


def output_results(poi_result_set, screen=True, outfile=None):
    """
    Outputs results to screen or csv file
    """
    assert not isinstance(poi_result_set, basestring), 'POI result set is not list or tuple'

    if screen:
        print "\nZOAs by POI"
        print "="*80,
        for poi in poi_result_set:                
            print "\nLocation:\t%s" % poi[s.NAME_KEY]
            print "Address:\t%s" % poi[s.ADDR_KEY]
            print "Neighborhood:\t%s" % poi[s.NBHD_KEY]
            print "Coordinates:\t%.4f, %.4f" % (poi[s.LAT_KEY], poi[s.LNG_KEY])
            print "ZOA ID:\t\t%d" % poi[s.ZOA_KEY] 
        
    if outfile:
        assert isinstance (outfile, str), "Outfile name is not a string: %r" % name
        if outfile[-4:] != '.csv': outfile += '.csv'
        with open(outfile, 'wb') as f:  # Just use 'w' mode in 3.x
            target = DictWriter(f, poi_result_set[0].keys())
            target.writeheader()
            target.writerows(poi_result_set)