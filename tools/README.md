## Tools

#### Geocoder Utility

Converts lat, long into real addresses (and back) using pygeocoder.
Slower but more robust in terms of tolerance of partial addresses
and level of formated information provided. This still makes use of 
Google's geocoding API V3.

```python   
: param -a : geocode address
: param -r : reverse geocode from lat-lng to address
: param -j : print full GeocoderResult object in json
``` 

To make a command line script:
- Move this file to `/usr/local/bin`
- Remove `.py` extention
- `chmod +x` filename
- Ensure `"/usr/local/bin"` is in your `PATH`


#### GeoJSON Utility

Simple helper script that converts CSV of Point of Interest to GeoJSON.
Useful for visualization or import in to Google, Leaflet, etc.

TODO add getopts to make this more generic