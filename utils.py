import json
import decimal
from sys import exit
#from geopy.distance import vincenty

def half_even(num_val, n_places=4):
    """
    ROUND_HALF_EVEN a point to n_places decimal places
    """
    if not 0 < n_places <= 8:
        print "Can only round to 1-8 decimal places. Defaulting to two"
        n_places = 2

    try:
        rounding = 10**int(-1 * n_places)
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


