# -*- coding: utf-8 -*-

import scrapy


class SpeltItem(scrapy.Item):
    url = scrapy.Field()
    document = scrapy.Field()
    encoding = scrapy.Field()
