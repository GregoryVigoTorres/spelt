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
