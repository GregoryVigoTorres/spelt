# Copyright (c) 2018 Gregory Vigo Torres
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
import lxml.html
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy_splash import SplashRequest

from spelt.items import SpeltItem


class SerializeSpider(CrawlSpider):
    name = "spelt"
    allowed_domains = []
    start_urls = []

    rules = (
        Rule(LinkExtractor(allow_domains=''),
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
