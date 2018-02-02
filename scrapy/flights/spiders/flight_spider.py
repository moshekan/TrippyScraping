from datetime import datetime

import scrapy

from flights.items import FlightItem
from flights.utils import AirportFinder


class BaseFlightSpider(scrapy.Spider):
    """docstring for BaseFlightSpider"""
    airline_name = 'BaseAirline'
    REQUEST_DATE_FORMAT = '%Y-%m-%d'
    RESPONSE_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'

    @classmethod
    def format_request_date(cls, time):
        if not isinstance(time, datetime):
            raise ValueError('{0} is not a datetime object'.format(time))
        return time.strftime(cls.REQUEST_DATE_FORMAT)

    @classmethod
    def validate_request_date_format(cls, time):
        try:
            datetime.strptime(time, cls.REQUEST_DATE_FORMAT)
            return True
        except Exception:
            return False

    @classmethod
    def formate_response_datetime(cls, datetime_str):
        datetime_obj = datetime.strptime(
            datetime_str, cls.RESPONSE_DATETIME_FORMAT)
        return FlightItem.format_datetime(datetime_obj)

    @classmethod
    def parse_response(cls, response):
        raise NotImplementedError()

    @classmethod
    def parse_flight(cls, flight_dict):
        raise NotImplementedError()

    @staticmethod
    def is_iata_code(string):
        return string.isalpha() and len(string) == 3

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

