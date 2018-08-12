# -*- coding: utf-8 -*-
import lxml.html
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy_splash import SplashRequest

from spelt.items import SpeltItem


class SerializeSpider(CrawlSpider):
    name = "spelt"
    allowed_domains = ['doc.scrapy.org']
    start_urls = ['https://doc.scrapy.org/en/latest/']

    rules = (
        Rule(LinkExtractor(allow_domains='doc.scrapy.org'),
             follow=True,
             callback='parse_item'),
    )

    def _build_request(self, rule, link):
        """Re-implemented from base class
           uses SplashRequest instead of Request
        """
        r = SplashRequest(url=link.url, callback=self._response_downloaded)
        self.logger.info(r)
        r.meta.update(rule=rule, link_text=link.text)
        return r

    def parse_errback(self, error):
        self.logger.error(repr(error))

    def parse_item(self, response):
        self.logger.info('[PARSING] {} {}'.format(response.status,
                                                  response.url))
        item = SpeltItem(document=response.text,
                         encoding=response.encoding,
                         url=response.url)
        yield item
