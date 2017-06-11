# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DataSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class ToutiaoItem(scrapy.Item):
    title = scrapy.Field()
    image_url = scrapy.Field()
    artical_url = scrapy.Field()
    source_url = scrapy.Field()
    source = scrapy.Field()
    title_hash = scrapy.Field()
    collect_time = scrapy.Field()
    artical_time = scrapy.Field()
    catagore = scrapy.Field()
    tag = scrapy.Field()

