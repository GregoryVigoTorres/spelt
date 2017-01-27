import logging
import os

from colorama import Fore, init, Style
init(autoreset=True)

class FileExportPipeline(object):
    def __init__(self):
        self.root = ''

    @classmethod
    def from_crawler(cls, crawler):
        logging.info('{}Data Root{}{}'.format(Fore.CYAN,
                                              crawler.settings.get('DATA_DIR'),
                                              Style.RESET_ALL))
        C = cls()
        C.root = crawler.settings.get('DATA_DIR')
        return C

    def process_item(self, item, spider):
        """
        save text to filename
        filename is from url
        I'm assuming urls must be unique
        i.e. I'm not scraping the same URL twice for different content

        """
        dest_path = os.path.join(self.root, item.get('filename'))

        with open(dest_path, mode='w') as fd:
            fd.write(item['text'])
            logging.info('{}saved {}{}'.format(Fore.CYAN,
                                               dest_path,
                                               Style.RESET_ALL))

        return item
