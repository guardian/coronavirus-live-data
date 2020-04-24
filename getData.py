# This script will get the latest data from the Jons Hopkins GitHub repo https://github.com/CSSEGISandData
# And also the latest case figures from the ArcGIS feature server

import simplejson as json
def getData():
	
	# Get time series data

	import requests

	files = [
	"time_series_covid19_deaths_global.csv",
	"time_series_covid19_confirmed_global.csv"
	]

	headers = {'Accept': 'application/vnd.github.v3.raw'}

	for path in files:
		url = "https://api.github.com/repos/CSSEGISandData/COVID-19/contents/csse_covid_19_data/csse_covid_19_time_series/{path}".format(path=path)
		print("Getting", path)
		r = requests.get(url, headers=headers)
		with open(path, 'w') as f:
			f.write(r.text)
			
	print("Files saved")

	# Get current case data

	latestUrl = "https://services1.arcgis.com/0MSEUqKaxRlEPj5g/ArcGIS/rest/services/ncov_cases/FeatureServer/1/query?where=1%3D1&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&resultType=none&distance=0.0&units=esriSRUnit_Meter&returnGeodetic=false&outFields=Province_State%2CCountry_Region%2CConfirmed%2CRecovered%2CDeaths&returnGeometry=true&featureEncoding=esriDefault&multipatchOption=xyFootprint&maxAllowableOffset=&geometryPrecision=&outSR=&datumTransformation=&applyVCSProjection=false&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnExtentOnly=false&returnQueryGeometry=false&returnDistinctValues=false&cacheHint=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset=&resultRecordCount=&returnZ=false&returnM=false&returnExceededLimitFeatures=true&quantizationParameters=&sqlFormat=none&f=json"

	r = requests.get(latestUrl)
	print(r)

	with open('latest.json', 'w') as f:
		json.dump(r.json(), f)
		

# un-comment to just download the files:
# getData()
	

