# -*- coding: utf-8 -*-
import logging
import re
from urllib.parse import urlparse, urlunparse

from colorama import Fore, Back, Style, init
init(autoreset=True)

import lxml.html
import scrapy
from scrapy_splash import SplashRequest

from .config import (block_elems,
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

    def parse_input_elem(self, elem):
        skip_types = ('hidden',
                      'checkbox',
                      'password')

        if elem.attrib.get('type') in skip_types:
            return ''

        text = ''
        text_c = elem.text_content().strip()

        placeholder = elem.attrib.get('placeholder')

        if placeholder:
            text += '[placeholder]'+placeholder.strip()+'\n'

        if text_c:
            text += text_c

        return text

    def strip_elems(self, exclude_elems):
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

    def serialize(self, elem):
        """
        return text for elem and its children
        with or without trailing new line, as appropriate
        """
        # skip comments and such
        if not isinstance(elem.tag, str):
            return ''

        if elem.tag in exclude_tags:
            return ''

        if elem.tag in ('input', 'textarea'):
            text_input = self.parse_input_elem(elem)
            if text_input:
                return text_input+'\n'

        # text content of the current element tree part
        content = ''

        # block elem as in block level HTML element
        if elem.tag in block_elems:
            if elem.text:
                if not elem.text.isspace():
                    content += elem.text

            if elem.tail:
                if not elem.tail.isspace():
                    content += ' '+elem.tail

            # we need a line break even if the elem has no text
            # ... it's easier to remove extra line breaks
            # than insert only the ones I want
            return content+'\n'
        else:
            # inline elem
            if elem.text and elem.text.isspace() is False:
                content += elem.text+' '

            if elem.tail and elem.tail.isspace() is False:
                content += elem.tail.lstrip()

        return content

    def serialize_elems(self, elems):
        """
        return serialized text from all elements
        """
        text = ''

        for i in elems:
            raw_text = [self.serialize(elem)
                        for elem in
                        i.iterdescendants()]

            elem_text = ''.join([i for i in
                                 raw_text
                                 if i])

            # singularize whitespace
            text += re.sub(self.wspace_rx,
                           lambda i: i.group(0)[0],
                           elem_text)
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

        doc = self.strip_elems_by_tag(doc)
        doc = self.strip_elems_by_selector(doc)

        elems = doc.xpath('.//body/*')

        if not len(elems):
            logging.info('{}[WARNING] No elements found in {}{}'.format(
                Fore.RED,
                response.url,
                Style.RESET_ALL))
            yield

        # All text from elements
        text = self.serialize_elems(elems)

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
