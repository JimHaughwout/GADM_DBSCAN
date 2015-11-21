import utils

DATA_FILE = "/Users/jim/DEV/gadm_scan/data/points_of_interest.csv"

measure_set = utils.import_measures(DATA_FILE)
for measure in measure_set:
    print "%s (%.4f, %.4f)" % (measure['name'], measure['lat'], measure['lng'])
