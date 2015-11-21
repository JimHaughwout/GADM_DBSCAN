import settings as s
import utils
import numpy as np


poi_set = utils.import_measures(s.DATA_FILE)


if s.DEBUG:
    for poi in poi_set:
        print "%s (%.4f, %.4f)" % (poi[s.NAME_KEY], 
            poi[s.LAT_KEY], poi[s.LNG_KEY])

    for poi_1 in poi_set:
        print "\nFROM %s" % poi_1[s.NAME_KEY]
        print "==================================="
        for poi_2 in poi_set:
            if poi_1 != poi_2:
                utils.dist_calc(poi_1, poi_2, mode='gadm')




