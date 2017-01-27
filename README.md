#Spelt
*just the words*

Serialize HTML content from a website into plain text using [Scrapy](https://doc.scrapy.org/en/latest/intro/overview.html) and [Splash](https://splash.readthedocs.io/en/stable/) via [scrapy-splash](https://github.com/scrapy-plugins/scrapy-splash).

**Spelt** follows links in a site to try and get every page reachable by a typical user. Plain text files are saved with filenames derived from the URL of the page. By default, it tries to get every bit of visible text, however it can be configured to skip elements (see Usage).
All whitespace is collapsed to a single instance of itself, e.g. 4 line breaks becomes just one.

**Splash** is a Javascript rendering service used to (hopefully) make it possible to scrape dynamic content and **Scrapy** is an asynchronous scraping framework. **Scrapy-splash** makes it easy to use them together.

In a later version, it will probably be possible to handle sites that require login credentials.


##Installation
Requires Python 3
It's been tested using 3.5 and 3.6, but other Python 3 versions will probably work.

Install Python dependencies: `pip install -r requirements.txt`
I always recommend using a virtual env e.g. `pyvenv venv`.

[Docker](https://www.docker.com/) is strongly recommended.


##Usage
If you want to use the `runsplash` script you need to have [Docker](https://www.docker.com/) installed.
I think this is by far the easiest way to run splash, but it's not the only way.
You may need to make runsplash executable. e.g. `chmod 755 runsplash`

If you don't use the `runsplash` script, be sure to check the Splash options in `settings.py`. Consult the [scrapy-splash](https://github.com/scrapy-plugins/scrapy-splash) docs for reference.

You can change `splash_args` in `config.py` to scrape a little faster or slower, which might be useful if Splash is timing out or it's taking too long to scrape. Optimal settings depend a lot on the network and site you're scraping. Consult the Splash docs for all available options.

Edit `spiders/serialize.py` to define the URL you want to scrape, or any other spider options, per the [Scrapy spider docs](https://doc.scrapy.org/en/latest/topics/spiders.html#scrapy-spider).

Edit `DATA_DIR` in `scraper/settings.py` to change the directory where the text will be saved.
All the other settings are explained in the [Scrapy docs](https://doc.scrapy.org/en/latest/topics/settings.html).

To start crawling `cd` into the directory with `scrapy.cfg` or a child directory of it and type `scrapy crawl serialize`.

Spelt serialization options are in `spiders/config.py`.
`block_elems` are block level HTML elements that should have a line break after their content: like a `<div>`, for example.
`exclude_elems` defines elements by tag name that are skipped entirely. You can skip all `<noscript>` elements, for example.
`exclude_selectors` is where you can define elements to exclude by CSS selector e.g. `['#footer', '.advertisement']`.
`splash_args` is mentioned above. See the [Splash](https://splash.readthedocs.io/en/stable/) docs for reference.


Copyright Gregory Vigo Torres, 2017
License GPL v.3
