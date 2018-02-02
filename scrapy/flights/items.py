# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field
from datetime import datetime

from flights.consts import flight_consts

class FlightItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    origin = Field()
    destination = Field()
    departure_datetime = Field()
    arrival_datetime = Field()
    adult_price = Field()
    currency_code = Field()
    provider = Field()
    carrier_code = Field()
    flight_number = Field()
    requires_membership = Field()

    @staticmethod
    def format_datetime(datetime_obj):
        return datetime_obj.strftime(flight_consts.FLIGHT_DATETIME_FORMAT)
