import json
import decimal
from sys import exit
import csv
#from geopy.distance import vincenty


def half_even(num_val, n_places=4):
    """
    ROUND_HALF_EVEN a point to n_places decimal places
    """
    if not 0 < n_places <= 8:
        print "Can only round to 1-8 decimal places. Defaulting to two"
        n_places = 2

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


def import_measures(source_csv, lat_col='lat', lng_col='lng', rounding=4):
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

        return measure_set