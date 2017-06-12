#!/usr/bin/python
# Filename: similarity_pair_push.py
# _*_ coding:utf-8 _*_

# 同一分类具有相同关键词两个文章的插入到相似度计算队列

import pymongo

client = pymongo.MongoClient(host='127.0.0.1', port=27017)
db = client['ArticalRecommend']

artical_tag = db.artical_tag.find_one({'tag':{'$exists':True}, 'is_similar_processed':{'$exists':False}})
if (not artical_tag):
    print("there is no artical limit to process.")
    exit(1)

artical_tag['is_similar_processed'] = 1
db.artical_tag.save(artical_tag)

articals = db.artical_tag.find({'tag':{'$in':artical_tag['tag']}, 'catagore':artical_tag['catagore'], 'a_id':{'$ne':artical_tag['a_id']}})
if (not articals):
    exit(0)

for artical in articals:
    if (not db.similar_queue.find_one({'a_id1':artical_tag['a_id'], 'a_id2':artical['a_id']})) and \
            (not db.similar_queue.find_one({'a_id2':artical_tag['a_id'], 'a_id1':artical['a_id']})):
        db.similar_queue.insert({'a_id1':artical_tag['a_id'], 'a_id2':artical['a_id']})

exit(0)