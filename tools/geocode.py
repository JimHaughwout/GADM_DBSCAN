#! /usr/bin/env python
"""
Converting lat, long into real addresses (and back) using pygeocoder.
Slower but more robust in terms of tolerance of partial addresses
and level of formated information provided. This still makes use of 
Google's geocoding API V3.
 
Dependency: pip install pygeocoder
  
: param -a : geocode address
: param -r : reverse geocode from lat-lng to address
: param -j : print full GeocoderResult object in json
 
To make a command line script:
- Move this file to /usr/local/bin
- Remove .py extention
- chmod +x filename
- Ensure "/usr/local/bin" is in your PATH
 
"""
 
from pygeocoder import Geocoder
import sys
from sys import argv
import json
 
def geocode_address(address="77 Massachusetts Avenue, Cambridge, MA"):
	""" 
	Geocode an address query
 
	:param string address: the address you which to encode
 
	Result is class GeocoderResult with following useful properties:
		lat, lng = result.coordinates
		latitude = result.latitude
		longitude = result.longitude
		street_number = result.street_number
		street = result.route
		city = result.city
		state = result.state
		province = result.province
		postal_code = result.postal_code
		country = result.country
		formatted_address = result.formatted_address
		valid_address is TRUE or FALSE
	"""
	try:
		result = Geocoder.geocode(address)
	except: #Catch all exceptions
		e = sys.exc_info()[1]
  		sys.exit("Geocoder %s for %s" % (e, address))
  	
	# Check if result is a valid address
	if result.valid_address:
		return result
	else:
		sys.exit("Error - encode_address: Address=%r is an invalid address." % 
			address)
		return None
 
def geodecode_coords(lat, lng):
	"""
	Convert lat, long info full address of class GeocoderResult
 
	:param float lat is latitude in degrees
	:param float lng is longitude in degrees
	"""
	try:
		# Convert to float in case you get whole value degrees
		result = Geocoder.reverse_geocode(float(lat), float(lng))
	except: #Catch all exceptions
		e = sys.exc_info()[1]
  		sys.exit("Reverse Geocode %s for %r and %r." % (e, lat, lng))
  	return result
 
 
 
 
# Check if help options passed
help_message = '''
Usage: %s -options [args]' % argv[0]
\t-r to reverse geocode arg[2]=latitude arg[3]=longitude'
\t-a to geocode arg[2]="address to geocode"'
\t-j to produce full json output vs simple output.
''' 
if (len(argv) == 1) or ('-h' in argv[1]):
	print help_message
	sys.exit()
 
# Determing encoding and output format
encoding = 'unknown'
output = 'simple'
if '-' in argv[1]:
	if 'r' in argv[1]:
		encoding = 'reverse'
	if 'a' in argv[1]:
		encoding = 'normal'
	if 'j' in argv[1]:
		output = 'full json'
 
# Get and verify input 
if encoding == 'reverse':
	if len(argv) != 4:
		print 'Format is %s %s latitude longitude' % (argv[0], argv[1])
		print 'You provided %d arguments' % len(argv)
		sys.exit()
	try:
		lat = float(argv[2])
		lng = float(argv[3])
	except:
		e = sys.exc_info()[0]
  		sys.exit('Error: Did not pass numbers for both latitude and longitude.')
 
  	if abs(lat) > 90:
		sys.exit('Error: Latitude of %f is out of range [-90, 90].' % lat)
	
	if abs(lng) > 180:
		sys.exit('Error: Longitude of %f is out of range [-180, 180].' % lng)
 
	result = geodecode_coords(lat, lng)
 
elif encoding == 'normal':
	if len(argv) != 3:
		print 'Format is %s %s "address to encode"' % (argv[0], argv[1])
		print 'You provided %d arguments' % len(argv)
		sys.exit()
 
	address = argv[2]
	result = geocode_address(address)
 
else: 
	print 'Could not process input, try: %s -help' % argv[0]
	sys.exit()
 
if output == 'full json':
	print json.dumps(result.raw, sort_keys=True, indent=2, separators=(',', ': '))
else:
	print '\nAddress: %s' % result.formatted_address
	print 'Lat, Long: %f %f' % (result.coordinates)
	print 'Street Number %s' % result.street_number
	print 'Street/Route: %s' % result.route
	print 'Postal Code: %s' % result.postal_code
	print 'Neighborhood: %s' % result.neighborhood
	print 'City/Locatlity: %s' % result.city
	print 'County (GADM Level 2): %s' % result.county
	print 'State/Province (GADM Level 1): %s' % result.state
	print 'Country: %s\n' % result.country