# scraper/medex/items.py

import scrapy


class GenericItem(scrapy.Item):
    name = scrapy.Field()
    url = scrapy.Field()
    brand_names_url = scrapy.Field()


class BrandItem(scrapy.Item):
    generic_name = scrapy.Field()
    generic_url = scrapy.Field()
    brand_names_url = scrapy.Field()

    brand_name = scrapy.Field()
    dosage_form = scrapy.Field()
    strength = scrapy.Field()
    company = scrapy.Field()
    pack_size_price = scrapy.Field()

    brand_detail_url = scrapy.Field()
    source_url = scrapy.Field()