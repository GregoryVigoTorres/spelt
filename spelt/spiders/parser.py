import re
from .spelt_opts import BLOCK_ELEMS


class Serializer():
    def __init__(self):
        self.cur_tag = None
        self.text = ''

    def start(self, tag, attrib):
        self.cur_tag = tag
        if attrib.get('placeholder'):
            self.text += attrib.get('placeholder')+'\n'

    def end(self, tag):
        if tag in BLOCK_ELEMS:
            self.text += '\n'

    def data(self, data):
        data = data.replace('\n', '')
        self.text += data


    def comment(self, text):
        pass

    def close(self):
        # try to fixed leading/trailing whitespace
        text = re.sub(' +', ' ', self.text)
        text = re.sub('\s+\n', '\n', text)
        text = re.sub('\n\s+', '\n', text)
        return text
