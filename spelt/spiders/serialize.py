# -*- coding: utf-8 -*-
import lxml.html
from scrapy import Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy_splash import SplashRequest

from spelt.items import SpeltItem


class SerializeSpider(CrawlSpider):
    name = "spelt"
    allowed_domains = ['scrapy.org']
    start_urls = ['https://docs.scrapy.org']

    rules = (
        Rule(LinkExtractor(allow_domains='docs.scrapy.org'),
             follow=True,
             callback='parse_item'),
    )

    encoding = 'utf-8'

    def start_requests(self):
        for url in self.start_urls:
            self.logger.info(url)
            yield Request(url,
                          callback=self.parse_item,
                          errback=self.parse_errback)
    #         yield SplashRequest(url, self.parse,
    #                             args=self.settings.get('SPLASH_ARGS'))

    def parse_errback(self, error):
        self.logger.error(repr(error))

    def parse_item(self, response):
        doc = lxml.html.fromstring(response.text)
        self.logger.info('[PARSING] {} {}'.format(response.status,
                                                  response.url))
        item = SpeltItem(document=doc,
                         encoding=response.encoding,
                         url=response.url)
        yield item
