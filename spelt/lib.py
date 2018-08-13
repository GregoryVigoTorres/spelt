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
import re

def line_wc(line):
    words = re.split('\s', line)
    words = [i for i in words if i and i.isspace() == False]
    chars = sum([len(w) for w in words])
    return len(words), chars

def count_words(text):
    lines = text.split('\n')
    wc = 0
    chars = 0
    line_count = len(lines)
    for line in lines:
        w, c = line_wc(line)
        wc += w
        chars += c

    return {'characters': chars,
            'words': wc,
            'lines': line_count}
