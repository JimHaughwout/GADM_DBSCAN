# Parameters for display and debug
ZOA_SUMMARY_TO_SCREEN = True
MATPLOT_ZOA_CLUSTERS = True

#MODE = 'basic-vicenty'
MODE = 'vincenty-gadm'  
#MODE = 'proxy'

DEBUG = False

# Set parameters for clustering
DEFAULT_RADIUS = 1.0
DEFAULT_ROUNDING = 4
LOCAL = 0.4
X_TOWN = 2.0

# Set these based on your input and output CSVs
INPUT_FILE = "/Users/jhaughwout/DEV/GADM_DBSCAN/data/points_of_interest.csv"
#OUTPUT_FILE = "/Users/jhaughwout/Desktop/zoa_results.csv"
OUTPUT_FILE = None

LAT_KEY = 'lat'
LNG_KEY = 'lng'
ADDR_KEY = 'address'
NBHD_KEY = 'neighborhood'
CITY_KEY = 'city'
NAME_KEY = 'name'
ZOA_KEY = 'zoa_id'