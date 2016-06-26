#!/usr/bin/env python

import requests
import json
from haversine import haversine
import datetime


class Route:
    def __init__(self, departure_airport, arrival_airport):
        self.departure_airport = departure_airport
        self.arrival_airport = arrival_airport
        self.distance = self.calc_distance()
        self.typical_duration = self.calc_typical_duration()

    def calc_distance(self):

        departure_coords = (self.departure_airport.lat, self.departure_airport.lon)
        arrival_coords = (self.arrival_airport.lat, self.arrival_airport.lon)

        distance_in_miles = haversine(departure_coords, arrival_coords, miles=True)

        return distance_in_miles

    def calc_typical_duration(self):

        # .117 denotes avg flight speed of 513mph. To check: 60 mins / .117 = 513
        duration = (0.117 * self.distance) + 43.2

        return duration


class Airport:

    def __init__(self, code, name, city, country_code, country, lat, lon):
        self.code = code
        self.name = name
        self.city = city
        self.country_code = country_code
        self.country = country
        self.lat = lat
        self.lon = lon


class Flight:
    # A flight as returned from the Flighttracks FLex API

    def __init__(self, id, departs, arrives, date, airline, flight_number, sched_block_mins, actual_block_mins,
                 sched_air_mins, actual_air_mins, sched_taxi_out, actual_taxi_out, sched_taxi_in, actual_taxi_in):
        self.id = id
        self.departs = departs
        self.arrives = arrives
        self.date = date
        self.airline = airline
        self.flight_number = flight_number
        self.scheduled_block_minutes = sched_block_mins
        self.actual_block_minutes = actual_block_mins
        self.scheduled_air_minutes = sched_air_mins
        self.actual_air_minutes = actual_air_mins
        self.scheduled_taxi_out = sched_taxi_out
        self.actual_taxi_out = actual_taxi_out
        self.scheduled_taxi_in = sched_taxi_in
        self.actual_taxi_in = actual_taxi_in


def find_airport(code):
    for airport in airport_data:
        if code == airport.code:
            return airport

def get_route_flights(api_url, format, auth, route_tracked, startdate, enddate):
    route_flights_endpoint = "/flightstatus/historical/rest/v2"

    date = startdate
    route_info = []
    airport_data = []
    flight_data = []

    departure_airport = find_airport(route_tracked["depart"])
    arrival_airport = find_airport(route["arrive"])

    route = Route(departure_airport, arrival_airport)

    if route not in route_info:
        route_info.append(route)

    stem_url = api_url + route_flights_endpoint + format

    while date <= enddate:
        response_json = flightstats_api_requests(stem_url, auth, route_tracked["depart"], route["arrive"], date)

        airports = response_json["appendix"]["airports"]

        for airport in airports:
            current_airport = Airport(
                airport["fs"],
                airport["name"],
                airport["city"],
                airport["countryCode"],
                airport["countryName"],
                airport["latitude"],
                airport["longitude"]
            )

            if current_airport not in airport_data:
                airport_data.append(current_airport)


        flights = response_json["flightStatuses"]
        # save flight fields to flights_data array

        for flight in flights:

            if len(flight["flightDurations"]) == 8:

                flight_data.append(Flight(
                    flight["flightId"],
                    flight["departureAirportFsCode"],
                    flight["arrivalAirportFsCode"],
                    flight["departureDate"]["dateUtc"],
                    flight["primaryCarrierFsCode"],
                    flight["flightNumber"],
                    flight["flightDurations"]["scheduledBlockMinutes"],
                    flight["flightDurations"]["blockMinutes"],
                    flight["flightDurations"]["scheduledAirMinutes"],
                    flight["flightDurations"]["airMinutes"],
                    flight["flightDurations"]["scheduledTaxiOutMinutes"],
                    flight["flightDurations"]["taxiOutMinutes"],
                    flight["flightDurations"]["scheduledTaxiInMinutes"],
                    flight["flightDurations"]["taxiInMinutes"]
                ))

            else:

                print "flightId " + str(flight["flightId"]) + " failed. Missing Flight Duration fields."



        # increment date
        date = date + datetime.timedelta(days=1)

    print str(len(airport_data)) + " airports found:"
    print json.dumps(airport_data, sort_keys=True, indent=4, separators=(',', ': '))

    print str(len(flight_data)) + " flights found:"
    print json.dumps(flight_data, sort_keys=True, indent=4, separators=(',', ': '))

    return flight_data


def flightstats_api_requests(api_url, auth, depature_airport, arrival_airport, date):
    route_url = ("/route/status/" + depature_airport + "/" + arrival_airport + "/dep/" + str(date.year) +
                 "/" + str(date.month) + "/" + str(date.day))

    params = auth + "&utc=true&maxFlights=100"

    request_url = api_url + route_url + params
    print "API request: " + request_url

    r = requests.get(request_url)
    flights_json = r.json()

    return flights_json


def flightstats_airport_api(api_url, auth, airport_code):

    request_url = api_url + "/" + airport_code + "/today" + auth

    r = requests.get(request_url)
    airport_data = r.json()

    return airport_data


def main():

    # Flightstats Flex API details
    api_url = "https://api.flightstats.com/flex"
    api_format = "/json"

    # Flightstats API authentication
    app_id = ""
    app_key = ""
    auth = "?appId=" + app_id + "&appKey=" + app_key

    # # Kimono Firebase for SkyTrax Airline Categories
    # firebase_url = "https://kimonolabs-ashm.firebaseio.com/"
    # airlines_4star = "/kimono/api/emfnmrma/latest.json?auth=HYaFix4rIPooOPQdzMrveJYvHpiHMwSM2XSmmhXL"
    # results = json.load(urllib.urlopen(airlines_4star))

    routes_to_track = [{"depart": "LHR", "arrive": "JFK"}]
    startdate = datetime.date(2016, 3, 6)
    enddate = datetime.date(2016, 3, 30)


    # Get 1 months worth of flight data for 1 route
    for route_to_track in routes_to_track:
        flights_data = get_route_flights(api_url, api_format, auth, route_to_track, startdate, enddate)
        route_data =


if __name__ == "__main__":
    main()