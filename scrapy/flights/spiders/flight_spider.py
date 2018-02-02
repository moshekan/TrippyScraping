from datetime import datetime

import scrapy

from flights.items import FlightItem
from flights.utils import AirportFinder
from flights.consts import flight_consts


class BaseFlightSpider(scrapy.Spider):
    """docstring for BaseFlightSpider"""
    airline_name = 'BaseAirline'

    def __init__(self, name=None, origin=None, dest=None, from_date=None, to_date=None, adults=None, children=None,
        is_roundtrip=None, length=None, **kwargs):
        super(BaseFlightSpider, self).__init__(name, **kwargs)
        self.origin = origin
        self.dest = dest
        self.from_date = from_date
        self.to_date = to_date
        self.adults = adults or flight_consts.DEFAULT_ADULT_COUNT
        self.children = children or flight_consts.DEFAULT_CHILDREN_COUNT
        self.is_roundtrip = is_roundtrip or flight_consts.DEFAULT_IS_ROUNDTRIP
        self.length = length or flight_consts.DEFAULT_TRIP_LENGTH

    @classmethod
    def format_request_date(cls, time):
        return time.strftime(cls.REQUEST_DATE_FORMAT)

    @classmethod
    def formate_response_datetime(cls, datetime_str):
        datetime_obj = datetime.strptime(
            datetime_str, cls.RESPONSE_DATETIME_FORMAT)
        return FlightItem.format_datetime(datetime_obj)

    @staticmethod
    def is_iata_code(string):
        return string.isalpha() and len(string) == flight_consts.IATA_CODE_LENGTH

    @staticmethod
    def get_origin_dest(origin, dest):
        origin_is_iata = BaseFlightSpider.is_iata_code(origin)
        dest_is_iata = BaseFlightSpider.is_iata_code(dest)

        if not (origin_is_iata and dest_is_iata):
            a = AirportFinder()
            if not origin_is_iata:
                origin = a.find_airport_code_by_string(origin)
            if not dest_is_iata:
                dest = a.find_airport_code_by_string(dest)

        return origin, dest

