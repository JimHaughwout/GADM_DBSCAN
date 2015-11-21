import settings
import utils


measure_set = utils.import_measures(settings.DATA_FILE)

if settings.DEBUG:
    for measure in measure_set:
        print "%s (%.4f, %.4f)" % (measure[settings.NAME_KEY], 
            measure[settings.LAT_KEY], measure[settings.LAT_KEY])
