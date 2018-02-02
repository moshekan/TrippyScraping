from datetime import datetime
import json

import scrapy

from flight_spider import BaseFlightSpider
from flights.items import FlightItem


WIZZ_REQUEST_TEMPLATE = {
    "flightList": [],
    "adultCount": "{0}",
    "childCount": 0,
    "infantCount": 0,
    "wdc": False,
    "dayInterval": 5,
}


class WizzairSpider(BaseFlightSpider):
    name = 'Wizzair'
    airline_name = 'Wizzair'
    REQUEST_DATE_FORMAT = '%Y-%m-%d'
    RESPONSE_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
    API_URL = 'https://be.wizzair.com/7.8.3/Api/search/search'

    @classmethod
    def parse_response(cls, response):
        data = json.loads(response.body.decode('utf-8'))
        flights = []
        if data['outboundFlights']:
            flights += data['outboundFlights']
        if data['returnFlights']:
            flights += data['returnFlights']

        for flight in flights:
            yield cls.parse_flight(flight)

    @classmethod
    def parse_flight(cls, flight_dict):
        flight = FlightItem()
        flight['origin'] = flight_dict['departureStation']
        flight['destination'] = flight_dict['arrivalStation']
        flight['departure_datetime'] = WizzairSpider.formate_response_datetime(
            flight_dict['departureDateTime'])
        flight['arrival_datetime'] = WizzairSpider.formate_response_datetime(
            flight_dict['arrivalDateTime'])
        flight_fares = flight_dict['fares'][0]['fullBasePrice']
        flight['adult_price'] = flight_fares['amount']
        flight['currency_code'] = flight_fares['currencyCode']
        flight['provider'] = cls.airline_name
        flight['flight_number'] = flight_dict['flightNumber']
        flight['carrier_code'] = flight_dict['carrierCode']
        flight['requires_membership'] = flight_dict['fares'][0]['wdc']
        return flight

    def start_requests(self):
        yield self.api_request('TLV', 'prague', '2018-01-29', 2, True)

    def _generate_flight_request_dict(self, origin, dest, date):
        flight = {}
        if isinstance(date, datetime):
            date = WizzairSpider.format_request_date(date)
        elif isinstance(date, str):
            WizzairSpider.validate_request_date_format(date)

        origin, dest = BaseFlightSpider.get_origin_dest(origin, dest)
        flight['departureStation'] = origin
        flight['arrivalStation'] = dest
        flight['departureDate'] = date
        return flight

    def _generate_wizzair_api_request_json(self, adult_count, wdc, flights):
        formdata = dict(WIZZ_REQUEST_TEMPLATE)
        formdata['flightList'] = flights
        formdata['wdc'] = wdc
        formdata['adultCount'] = adult_count
        return formdata

    def api_request(self, origin, dest, date, adult_count, wdc=False):
        """
        Sends the Request Wizzair's Api and returns the request.
        """

        flights = []
        flights.append(self._generate_flight_request_dict(origin, dest, date))
        formdata = self._generate_wizzair_api_request_json(
            adult_count, wdc, flights)

        request = scrapy.Request(WizzairSpider.API_URL,
                                 method='POST',
                                 body=json.dumps(formdata),
                                 headers={'Content-Type': 'application/json'},
                                 callback=self.parse_response)
        return request
