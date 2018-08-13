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
