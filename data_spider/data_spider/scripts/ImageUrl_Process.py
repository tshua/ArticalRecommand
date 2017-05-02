#!/usr/bin/python
# Filename: ImageUrl_Process.py

import pymongo


def update_item(line, db):
    line = line.split('|')
    db['artical'].update({'title':line[0]}, {'$set':{'image_url':line[1], 'source_url':line[2]}})

#db.Account.update({"UserName":"libing"},{"$set":{"Email":"libing@126.com","Password":"123"}})

client = pymongo.MongoClient(host='127.0.0.1', port=27018)
db = client['ArticalRecommend']

with open("tmp_imageurl.txt") as f:
    for line in f:
        update_item(line, db)