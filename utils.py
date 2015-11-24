import settings as s
import decimal
from csv import DictReader, DictWriter, writer
from sys import exit
import numpy as np
from sklearn import metrics
import matplotlib.pyplot as plt


def get_name_list(poi_set):
    """
    Returns list of names of POIs in order of appearance in set
    """
    assert not isinstance(poi_set, basestring), 'POI set is not list or tuple'

    poi_names = list()
    for poi in poi_set:
        poi_names.append(poi[s.NAME_KEY])

    return(poi_names)


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


def plot_results(labels, X, core_samples_mask):
    """
    TODO
    """
    print "\nPlotting Graph"
    print "="*80
    
    # Black removed and is used for noise instead.
    unique_labels = set(labels)
    colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))

    fig = plt.figure()
    ax = fig.add_subplot(111)

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

    plt.title('Estimated number of clusters: %d' % len(unique_labels))
    plt.show()


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
        with open(outfile, 'wb') as f:
            target = DictWriter(f, poi_result_set[0].keys())
            target.writeheader()
            target.writerows(poi_result_set)
        print "\nWrote output to %s.\n" % outfile