import re
from .spelt_opts import BLOCK_ELEMS


class Serializer():
    def __init__(self):
        self.cur_tag = None
        self.text = ''

    def start(self, tag, attrib):
        self.cur_tag = tag

    def end(self, tag):
        if tag in BLOCK_ELEMS:
            self.text += '\n'

    def data(self, data):
        if data.isspace() is False:
            data = data.strip()
            self.text += re.sub('\s+', ' ', data)+' '

    def comment(self, text):
        pass

    def close(self):
        return self.text

