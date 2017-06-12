# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo

class DataSpiderPipeline(object):
    def process_item(self, item, spider):
        return item

class InsertToutiaoToMongo(object):
    artical_name = 'artical'
    artical_tag_name = 'artical_tag'


    def __init__(self, mongo_host, mongo_port, mongo_db):
        self.mongo_host = mongo_host
        self.mongo_port = mongo_port
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_host=crawler.settings.get('MONGO_HOST'),
            mongo_port=crawler.settings.get('MONGO_PORT'),
            mongo_db = crawler.settings.get('MONGO_DB'),
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(host=self.mongo_host, port=self.mongo_port)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if (self.db[self.artical_name].find_one({'title_hash':item['title_hash']})):
            return item
        artical =  dict(item)
        artical_tag = {}
        artical_tag['tag'] = artical['tag']
        # artical_tag['catagore'] = artical['catagore']

        del(artical['tag'])
        # del(artical['catagore'])
        a_id = self.db[self.artical_name].insert(artical)

        artical_tag['a_id'] = str(a_id)
        self.db[self.artical_tag_name].insert(artical_tag)
        return item