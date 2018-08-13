# Spelt
*just the words*
*Version 2.0*

Serialize HTML content from a website into plain text using [Scrapy](https://doc.scrapy.org/en/latest/intro/overview.html) and [Splash](https://splash.readthedocs.io/en/stable/) via [scrapy-splash](https://github.com/scrapy-plugins/scrapy-splash).

**Spelt** crawls a site to try and locate every visible page. The URL structure of the website is maintained in the saved data. By default, all the visible text or every HTML element is extracted, however elements can be skipped (see Usage).

**Splash** is a Javascript rendering service used to (hopefully) make it possible to scrape dynamic content and **Scrapy** is an asynchronous scraping framework. **Scrapy-splash** makes it easy to use them together.


## Installation
Tested with Python 3.6.
At the time of writing, Spelt doesn't work with Python 3.7 due to incompatibilities with dependencies.

Using a virtual environment is always recommended.
`python3 -m venv venv`
`. venv/bin/activate`
Install Python dependencies: `pip install -r requirements.txt`

Splash and scrapy-splash are required. Docker is recommended.
See the Docker, Splash and scrapy-splash docs for more information.


## Usage
Version 2.0
If you want to use the `runsplash` script you need to have [Docker](https://www.docker.com/) installed.
This is the easiest way to run splash, but it's not the only way. See the Splash and scrapy-splash docs for more information.
You may need to make runsplash executable with `chmod 755 runsplash`.

If you don't use the `runsplash` script, be sure to verify the Splash options in `settings.py`. Consult the [scrapy-splash](https://github.com/scrapy-plugins/scrapy-splash) docs for reference.

You can change `splash_args` in `settings.py` (see [Splash docs](https://splash.readthedocs.io/en/stable/) for reference) to e.g. scrape a little faster or slower, which might be useful if Splash is timing out or it's taking too long to scrape. Optimal settings depend a lot on the network and site you're scraping. See the Splash docs for more information.

Edit `spiders/serialize.py` to define the URL you want to scrape, or any other spider options, per the [Scrapy spider docs](https://doc.scrapy.org/en/latest/topics/spiders.html#scrapy-spider).
**Be sure to define `allowed_urls` or `deny` in the rules unless you want to scrape the entire internet.**

**Spelt** is a pretty generic Scrapy project, so consult the Scrapy docs for all possible options.

Define `DATA_DIR` in `scraper/settings.py` to set the directory where the text or html will be saved.
Other configuration options in `scraper/settings.py` are:
`SAVE_HTML` :Bool
`SAVE_PLAIN_TEXT` :Bool
`COUNT_WORDS` :Bool count characters, words and lines
`STATS_PATH` :Str file where the character, word and line count will be saved

Spelt serialization options are in `spiders/spelt_opts.py`.
`BLOCK_ELEMS` are block level HTML elements that should have a line break after their content, like a `<div>`.
`EXCLUDE_ELEMS` defines elements by tag name that are skipped entirely. You can skip all `<video>` elements, for example.
`EXCLUDE_SELECTORS` is where you can define elements to be excluded, along with all their children, using CSS selectors e.g. `['#footer', '.advertisement']`.

To start crawling run `scrapy crawl spelt`.


Copyright Gregory Vigo Torres, 2018
License GPL v.3
