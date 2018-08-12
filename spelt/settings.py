import os
# Scrapy settings for spelt
BOT_NAME = 'spelt'

# keep Scrapy from logging too much
LOG_LEVEL = 'INFO'

SPIDER_MODULES = ['spelt.spiders']
NEWSPIDER_MODULE = 'spelt.spiders'

USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; rv:61.0) Gecko/20100101 Firefox/61.0'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

COOKIES_ENABLED = True

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}
SPLASH_URL = 'http://0.0.0.0:8050'

# args for splash requests
# see splash docs for reference
# Try changing this if you're getting splash timeout errors
SPLASH_ARGS = {'wait': 0.5,
               'timeout': 30,
               'images_enabled': False}

SPIDER_MIDDLEWARES = {
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
    'scrapy.spidermiddlewares.referer.RefererMiddleware': 200,
}

DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'

DOWNLOADER_MIDDLEWARES = {
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 0
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'

#Spelt options
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(root, 'data')
if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)

STATS_PATH = os.path.join(DATA_DIR, 'stats.json')

SAVE_HTML = True
SAVE_PLAIN_TEXT = True
COUNT_WORDS = True

ITEM_PIPELINES = {
   'spelt.pipelines.FileExportPipeline': 300,
}
