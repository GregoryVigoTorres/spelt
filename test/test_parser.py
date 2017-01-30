import re

from scrapy.http.response.text import TextResponse

from spelt.spiders import serialize

# run as python -m pytest test from project root

def test_block_elem_with_children():
    """
    tests 2 block elems with children
    ignores trailing whitespace
    """
    spider = serialize.SerializeSpider()

    fake_response = TextResponse(encoding='utf-8',
                                 url='https://doc.scrapy.org')

    with open('test/data/block_elem.html', mode='rb') as fd:
        body = fd.read()
        fake_response._set_body(body)

    item = spider.parse(fake_response)
    text = next(item).get('text')

    with open('test/data/block_elem.txt') as fd:
        test_text = fd.read()

    # ignore trailing whitespace
    text = re.sub('\n\s', '\n', text).strip()
    test_text = re.sub('\n\s', '\n', test_text).strip()

    assert text == test_text

def test_skip_elems_by_tag():
    """
    make sure elems are skipped by tag name e.g. script
    """
    spider = serialize.SerializeSpider()
    fake_response = TextResponse(encoding='utf-8',
                                 url='https://doc.scrapy.org')

    spider.exclude_tags.append('footer')

    with open('test/data/skip_by_tag.html', mode='rb') as fd:
        body = fd.read()
        fake_response._set_body(body)

    item = spider.parse(fake_response)
    text = next(item).get('text').strip()

    with open('test/data/skip_by_tag.txt') as fd:
        test_text = fd.read().strip()

    # ignore trailing whitespace
    text = re.sub('\n\s', '\n', text).strip()
    test_text = re.sub('\n\s', '\n', test_text).strip()

    assert text == test_text

def test_skip_elems_by_selector():
    """
    should test for nested elements that should have been removed
    i.e. if a class='link' should be skipped when inside a
    parent element that is not skipped
    """
    spider = serialize.SerializeSpider()
    fake_response = TextResponse(encoding='utf-8',
                                 url='https://doc.scrapy.org')

    spider.exclude_selectors = ['.skip-elem']

    with open('test/data/skip_by_selector.html', mode='rb') as fd:
        body = fd.read()
        fake_response._set_body(body)

    item = spider.parse(fake_response)
    text = next(item).get('text').strip()

    with open('test/data/skip_by_selector.txt') as fd:
        test_text = fd.read().strip()

    # ignore trailing whitespace
    text = re.sub('\n\s', '\n', text).strip()
    test_text = re.sub('\n\s', '\n', test_text).strip()

    assert text == test_text

def test_form_input():
    spider = serialize.SerializeSpider()
    fake_response = TextResponse(encoding='utf-8',
                                 url='https://doc.scrapy.org')

    with open('test/data/form.html', mode='rb') as fd:
        body = fd.read()
        fake_response._set_body(body)

    item = spider.parse(fake_response)
    text = next(item).get('text').strip()

    with open('test/data/form.txt') as fd:
        test_text = fd.read().strip()

    # ignore trailing whitespace
    text = re.sub('\n\s', '\n', text).strip()
    test_text = re.sub('\n\s', '\n', test_text).strip()

    assert text == test_text

