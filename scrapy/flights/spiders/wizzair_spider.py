from datetime import datetime, timedelta
import json

import scrapy

from flight_spider import BaseFlightSpider
from flights.items import FlightItem


WIZZ_REQUEST_TEMPLATE = {
    "flightList": [],
    "adultCount": "{0}",
    "childCount": "{0}",
    "infantCount": 0,
    "wdc": False,
    "dayInterval": 5,
}


class WizzairSpider(BaseFlightSpider):
    name = 'wizzair'
    airline_name = 'Wizzair'
    REQUEST_DATE_FORMAT = '%Y-%m-%d'
    RESPONSE_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
    API_URL = 'https://be.wizzair.com/7.8.5/Api/search/search'

    @classmethod
    def parse(cls, response):
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
        self.from_date = datetime.now()
        self.to_date = datetime.now() + timedelta(days=1)
        self.origin = 'TLV'
        self.dest = 'PRG'
        self.adults = 2
        self.is_roundtrip = True
        self.length = 5

        if not (self.from_date and self.to_date and self.origin and self.dest):
            raise ValueError('Some Fields are missing')

        self.dest, self.origin = BaseFlightSpider.get_origin_dest(self.origin, self.dest)
        days_infront = (self.to_date - self.from_date).days + 1
        date_list = [self.from_date + timedelta(days=x) for x in range(0, days_infront)]
        for date in date_list:
            yield self.api_request(date)

    @staticmethod
    def _generate_flight_request_dict(origin, dest, date):
        flight = {}
        formatted_date = WizzairSpider.format_request_date(date)
        flight['departureStation'] = origin
        flight['arrivalStation'] = dest
        flight['departureDate'] = formatted_date
        return flight

    @staticmethod
    def _generate_wizzair_api_request_json(adult_count, child_count, wdc, flights):
        formdata = dict(WIZZ_REQUEST_TEMPLATE)
        formdata['flightList'] = flights
        formdata['wdc'] = wdc
        formdata['adultCount'] = adult_count
        formdata['childCount'] = child_count
        return formdata

    def api_request(self, date, wdc=False):
        """
        Sends the Request Wizzair's Api and returns the request.
        """

        flights = [WizzairSpider._generate_flight_request_dict(self.origin, self.dest, date)]
        if self.is_roundtrip:
            flights.append(WizzairSpider._generate_flight_request_dict(self.dest, self.origin,
                                                                       date + timedelta(days=self.length)))
        form_data = WizzairSpider._generate_wizzair_api_request_json(
            self.adults, self.children, wdc, flights)

        print form_data
        request = scrapy.Request(WizzairSpider.API_URL,
                                 method='POST',
                                 body=json.dumps(form_data),
                                 headers={'Content-Type': 'application/json'},
                                 callback=self.parse)
        return request
