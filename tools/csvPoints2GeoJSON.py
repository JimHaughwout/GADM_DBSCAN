#! /usr/bin/env python
"""
Simple helper script that converts CSV of Point of Interest to GeoJSON.
Useful for visualization or import in to Google, Leaflet, etc.

TODO add getopts to make this more generic
"""

import sys
import json
import csv
import getopt

# TODO need to make these dynamic
NAME_KEY = 'name'
ADDR_KEY = 'address'
NBHD_KEY = 'neighborhood'
LAT_KEY = 'lat'
LNG_KEY = 'lng'

def print_usage_and_exit(msg=None):
    """ 
    Pretty print exit on error
    """
    print "\nUsage: %s [-s][-h]" % sys.argv[0]
    print "\t-h Print usage help"
    print "\t-s Source CSV file - Required"
    if msg: print msg + "\n"
    sys.exit(2)


def extract_poi(poi):
    """
    Check if data has desired keys

    TODO - make this generic
    """
    try: 
        name = poi[NAME_KEY]
        addr = poi[ADDR_KEY]
        nbhd = poi[NBHD_KEY]
        lat = float(poi[LAT_KEY])
        lng = float(poi[LNG_KEY])

        return name, addr, nbhd, lat, lng
 
    except (ValueError, KeyError, TypeError) as e:
        print_usage_and_exit(("%r is not in correct format: %s" % (row, e)))


# Parse opts, ensure we have required opts to determine mode, source, target
infile = None
try:
    opts, args = getopt.getopt(sys.argv[1:], "hs:")
    if not opts:
        print_usage_and_exit('No options supplied')
except getopt.GetoptError:
    print_usage_and_exit('Could not parse options')

for opt, arg in opts:
    if opt == '-h':
        print_usage_and_exit()   
    elif opt == '-s':
        infile = arg


if not(infile):
    print_usage_and_exit('-s source_file not specified')
elif infile[-4:] != '.csv':
    print_usage_and_exit('source_file is not a .csv file')
else:
    outfile = infile[:-4] + '_geo.json'


# Try to open source file and extact events
try:
    data = list()
    with open(infile) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
except IOError as e:
    print_usage_and_exit(("Could not open %r to read: %s" % (infile, e)))

# Try to open target file
try:
    target = open(outfile, 'w')
except IOError as e:
    print_usage_and_exit(("Could not open %r to write: %s" % (outfile, e)))


# Loop through reads, parse into a data row, then write data row to CSV
row_count = 0
feature_count = 0

# Build list to hold GeoJSON features
features = list()

for row in data:
    row_count += 1

    name, addr, nbhd, lat, lng = extract_poi(row)
    coordinates = [lng, lat]

    # Build GeoJSON Feature from feature elements and append to list
    properties = {"name":name, "address":addr, "neighborhood":nbhd, "latitude":lat, "longitude":lng}
    geometry = {"type":"Point", "coordinates": coordinates}
    feature = {"type":"Feature", "properties":properties, "geometry":geometry}
    features.append(feature)

    feature_count += 1

# Assemble GeoJSON object as dictionary
geo_json = {"type":"FeatureCollection", "features":features}
output = json.dumps(geo_json, sort_keys=False, indent=2, separators=(',', ' : '))
target.write(output)
target.closed

# Tell user done and print stats
print "SUCCESS: Processed %d rows. Created %d GeoJSON features in %s\n" % (row_count, feature_count, outfile)