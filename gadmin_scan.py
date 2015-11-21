import settings
import utils


poi_set = utils.import_measures(settings.DATA_FILE)

if settings.DEBUG:
    for poi in poi_set:
        print "%s (%.4f, %.4f)" % (poi[settings.NAME_KEY], 
            poi[settings.LAT_KEY], poi[settings.LNG_KEY])

    for poi_1 in poi_set:
        print "\nFROM %s" % poi_1[settings.NAME_KEY]
        print "==================================="
        for poi_2 in poi_set:
            if poi_1 != poi_2:
                utils.dist_calc(poi_1, poi_2, mode='gadm')

