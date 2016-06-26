import requests
import json

def main():
	r = requests.get('https://api.flightstats.com/flex/flightstatus/historical/rest/v2/json/route/status/LHR/JFK/dep/2016/3/1?appId=0c4a4c9e&appKey=7129915a34f197c18257b76b1c958649&utc=true&maxflights=100')
	flight_data = r.json()

	print json.dumps(flight_data, sort_keys=True, indent=4, separators=(',', ': '))

if __name__ == "__main__":
    main()