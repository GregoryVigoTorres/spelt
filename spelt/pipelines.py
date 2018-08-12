import logging
import os
import re
from urllib.parse import urlparse, quote_plus

from lxml import etree
from colorama import Fore, init, Style
from spelt.spiders.spelt_opts import EXCLUDE_TAGS, EXCLUDE_SELECTORS


init(autoreset=True)
log = logging.getLogger(__name__)


class FileExportPipeline(object):
    @classmethod
    def from_crawler(cls, crawler):
        log.info('{}Data Root{}{}'.format(Fore.CYAN,
                                          crawler.settings.get('DATA_DIR'),
                                          Style.RESET_ALL))
        C = cls()
        C.data_root = crawler.settings.get('DATA_DIR')
        assert os.path.exists(C.data_root)
        C.save_html = crawler.settings.get('SAVE_HTML')
        C.save_text = crawler.settings.get('SAVE_PLAIN_TEXT')

        if not C.save_html or C.save_text:
            log.warn('Data will not be saved.\nYou must specify SAVE_HTML or SAVE_PLAIN_TEXT.')

        C.exclude_tags = EXCLUDE_TAGS
        C.exclude_selectors = EXCLUDE_SELECTORS
        return C

    def get_filenames(self, url):
        """Percent encoded url is filename
        But, slashes are kept so the directory structure can be reproduced"""
        url_info = urlparse(url)
        fn_base = '{netloc}{path}{params}{query}'.format(
            netloc=url_info.netloc,
            path=url_info.path,
            params=url_info.params,
            query=url_info.query
        )
        base = quote_plus(fn_base, safe='/')
        base = os.path.splitext(base)[0]
        base = base.rstrip('/')
        return (os.path.join(self.data_root, base + '.txt'),
                os.path.join(self.data_root, base + '.html'))

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

    def save_to_file(self, fn, content):
        pardir = os.path.dirname(fn)

        try:
            os.makedirs(pardir)
        except FileExistsError as E:
            pass

        with open(fn, mode='w') as fd:
            fd.write(content)
            logging.info('{}saved {}{}'.format(Fore.CYAN,
                                               fn,
                                               Style.RESET_ALL))

    def process_item(self, item, spider):
        """
        Save extracted text and potentially raw HTML from scraped URL
        to a file
        """
        if not item:
            return item

        txt_path, html_path = self.get_filenames(item.get('url'))

        doc = item['document']
        doc = self.strip_elems_by_tag(doc)
        doc = self.strip_elems_by_selector(doc)

        if self.save_text:
            txt_content = doc.text_content()
            txt_content = re.sub('\s\s+', lambda i: i.group(0)[0], txt_content)
            self.save_to_file(txt_path, txt_content)

        if self.save_html:
            html_content = etree.tostring(doc, pretty_print=True)
            html_content = html_content.decode(encoding=item['encoding'])
            self.save_to_file(html_path, html_content)

        return item
