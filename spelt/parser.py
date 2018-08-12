from html import unescape
import re
from spelt.spelt_opts import BLOCK_ELEMS


class SerializeParser():
    def __init__(self):
        self.cur_tag = None
        self.text = ''

    def start(self, tag, attrib):
        self.cur_tag = tag
        if attrib.get('placeholder'):
            self.text += attrib.get('placeholder')+'\n'

        if attrib.get('alt'):
            self.text += attrib.get('alt')+'\n'

    def end(self, tag):
        if tag in BLOCK_ELEMS:
            self.text += '\n'

    def data(self, data):
        data = data.replace('\n', ' ')
        self.text += data

    def comment(self, text):
        pass

    def close(self):
        text = re.sub('(\s\s+)', lambda m: m.groups(0)[0], self.text)
        text = unescape(text)
        self.text = ''
        self.cur_tag = None
        return text
