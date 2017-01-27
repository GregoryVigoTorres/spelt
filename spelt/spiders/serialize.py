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

    def serialize(self, body):
        """
        get text for elements

        Tags are removed from inline elements
        so their text/tail gets moved to their parent.

        I know the placeholders for form elements
        is not quite right.
        """
        for el in body.iterdescendants():
            # skip comments and such
            if not isinstance(el.tag, str):
                continue

            text = ''
            placeholders = []

            for child in el.iterdescendants():
                placeholder = child.get('placeholder')
                if placeholder:
                    placeholders.append(placeholder)
                    # make sure we don't get placeholders more than once
                    child.set('placeholder', None)

                if child.tag not in block_elems:
                    child.drop_tag()

            text += ' '.join(placeholders)
            txt = el.text or ''
            tail = el.tail or ''
            text += txt.strip() + tail.strip()
            text = re.sub('\s+', ' ', text)
            yield text

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

        doc = self.strip_elems_by_tag(doc)
        doc = self.strip_elems_by_selector(doc)

        body = doc.xpath('./body')

        if not len(body):
            logging.info('{}[WARNING] No elements found in {}{}'.format(
                Fore.RED,
                response.url,
                Style.RESET_ALL))
            yield

        elem_text = self.serialize(body[0])
        text = '\n'.join([i for i in elem_text if i])

        if not text:
            logging.info('{}[ERROR] No text found {}{}'.format(
                Fore.RED,
                response.url,
                Style.RESET_ALL))
            yield

        fn = self.get_filename(response)

        yield {'filename': fn,
               'text': text}

        # get links to follow
        links = self.extract_links(doc, response)

        for url in links:
            yield SplashRequest(url,
                                self.parse,
                                args=self.settings.get('SPLASH_ARGS'))
