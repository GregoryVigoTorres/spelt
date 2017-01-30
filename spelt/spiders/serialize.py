# -*- coding: utf-8 -*-
import logging
import re
from urllib.parse import urlparse, urlunparse

from colorama import Fore, Back, Style, init
init(autoreset=True)

import lxml.html
from lxml import etree
import scrapy
from scrapy_splash import SplashRequest

from .spelt_opts import (block_elems,
                         exclude_tags,
                         exclude_selectors)


class Serializer():
    def __init__(self):
        self.cur_tag = None
        self.text = ''

    def start(self, tag, attrib):
        self.cur_tag = tag

    def end(self, tag):
        if tag in block_elems:
            self.text += '\n'

    def data(self, data):
        if data.isspace() is False:
            data = data.strip()
            self.text += re.sub('\s+', ' ', data)+' '

    def comment(self, text):
        pass

    def close(self):
        return self.text


class SerializeSpider(scrapy.Spider):
    name = "spelt"
    allowed_domains = []
    start_urls = ['https://doc.scrapy.org/en/latest/topics/settings.html']
    link_urls = []
    exclude_selectors = exclude_selectors
    exclude_tags = exclude_tags
    wspace_rx = re.compile('(\s+)|(\t+)|(\n+)')
    encoding = 'utf-8'

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse,
                                args=self.settings.get('SPLASH_ARGS'))

    def extract_links(self, doc, response):
        """
        only get local links
        """
        links = doc.xpath('.//a')

        base_url = urlparse(response.url)

        def gen_links(links):
            for i in links:
                href = i.attrib.get('href')

                if not href:
                    continue

                if 'mailto' in href:
                    continue

                if href in self.link_urls:
                    continue

                # get real URLs for relative HREFs
                parsed_url = urlparse(href)

                if not parsed_url.scheme or parsed_url.netloc:
                    href = urlunparse((base_url.scheme,
                                       base_url.netloc,
                                       parsed_url.path,
                                       parsed_url.params,
                                       parsed_url.query,
                                       parsed_url.fragment))

                yield href

        hrefs = list(gen_links(links))
        self.link_urls.extend(hrefs)
        return set(hrefs)

    def strip_elems(self, exclude_elems):
        """
        removes elements from doc tree
        """
        for E in exclude_elems:
            try:
                E.getparent().remove(E)
                logging.info('{}dropped: {}{}'.format(Fore.RED,
                                                      E,
                                                      Style.RESET_ALL))
            except Exception as E:
                logging.info(E)

    def strip_elems_by_selector(self, doc):
        for sel in self.exclude_selectors:
            exclude_elems = doc.cssselect(sel)
            self.strip_elems(exclude_elems)
        return doc

    def strip_elems_by_tag(self, doc):
        for tag in self.exclude_tags:
            arg = './/{}'.format(tag)
            exclude_elems = doc.xpath(arg)
            self.strip_elems(exclude_elems)
        return doc

    def get_filename(self, response):
        """
        filename for serialized text
        """
        fn = response.url.rstrip('/')+'.txt'
        fn = fn.replace('http://', '').\
                replace('https://', '').\
                replace('www.', '').\
                replace('/', '_')

        if len(fn) > 90:
            fn = fn[0:86]+'.txt'

        return fn

    def serialize(self, doc):
        """
        remove elements
        return serialized text
        """
        doc = self.strip_elems_by_tag(doc)
        doc = self.strip_elems_by_selector(doc)
        HTML = etree.tostring(doc, encoding=self.encoding)
        HTML = HTML.decode(encoding=self.encoding)
        Parser = etree.HTMLParser(target=Serializer())
        text = etree.HTML(HTML, Parser)
        return text

    def parse(self, response):
        """
        serialize text from HTML response
        """

        try:
            doc = lxml.html.fromstring(response.text)
            logging.info('[PARSING] {} {}'.format(response.status,
                                                  response.url))
        except Exception as E:
            logging.info('{}[ERROR] {} cannot be parsed{}'.format(
                Fore.RED,
                response.url,
                Style.RESET_ALL))
            logging.info(E)
            yield

        enc_elem = doc.xpath('.//meta[@charset]')
        if enc_elem:
            self.encoding = enc_elem[0].get('charset')

        text = self.serialize(doc)

        if not text:
            logging.info('{}[ERROR] No text found {}{}'.format(
                Fore.RED,
                response.url,
                Style.RESET_ALL))
            yield

        fn = self.get_filename(response)

        yield {'filename': fn,
               'html': response.text,
               'text': text}

        # get links to follow
        # links = self.extract_links(doc, response)
        #
        # for url in links:
        #     yield SplashRequest(url,
        #                         self.parse,
        #                         args=self.settings.get('SPLASH_ARGS'))
