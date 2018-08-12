# -*- coding: utf-8 -*-
import lxml.html
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
        doc = lxml.html.fromstring(response.text)
        self.logger.info('[PARSING] {} {}'.format(response.status,
                                                  response.url))
        item = SpeltItem(document=doc,
                         encoding=response.encoding,
                         url=response.url)
        yield item
