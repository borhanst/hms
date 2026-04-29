# scraper/medex/settings.py

BOT_NAME = "medex"

SPIDER_MODULES = ["medex.spiders"]
NEWSPIDER_MODULE = "medex.spiders"

ROBOTSTXT_OBEY = True

DOWNLOAD_DELAY = 0.5
CONCURRENT_REQUESTS = 8
CONCURRENT_REQUESTS_PER_DOMAIN = 4

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0 Safari/537.36"
)

ITEM_PIPELINES = {
    "medex.pipelines.MedexPipeline": 300,
}

LOG_LEVEL = "INFO"

RETRY_ENABLED = True
RETRY_TIMES = 3

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 0.5
AUTOTHROTTLE_MAX_DELAY = 5
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0

TWISTED_REACTOR = "twisted.internet.epollreactor.EPollReactor"
