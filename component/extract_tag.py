#!/usr/bin/python
# Filename: bayes_sort.py

import sys
sys.path.append('../')

import jieba
import jieba.analyse
from optparse import OptionParser
from bson import ObjectId
import pymongo
import re


def removeLabel(content): # 去除标签 \ 空格 \ 换行 \ tab
    dr = re.compile(r'<[^>]+>',re.S)
    dd = dr.sub('', content)
    dd = dd.replace("\n",'').replace(' ','').replace("\t",'').replace(".","_")
    # print(dd)
    return dd

def jiebacut(content): # 分词
    seg_list = jieba.cut(content,cut_all=False)
    tmp = []
    for seg in seg_list:
        tmp.append(seg)
    seg_list = tmp
    # print("jieba cut result:", "/ ".join(seg_list))
    return seg_list

def removeStopWords(word_list): # 删除停词
    with open("stopwords.txt", "r") as f:
        for line in f:
            line = line.replace("\n", '')
            while(1):
                if (line in word_list):
                    word_list.remove(line)
                    # print("remove" + line)
                else:
                    break
    # print("remove stop words result:", "/ ".join(word_list))
    return word_list

topK = 5 # 找出5个关键字

client = pymongo.MongoClient(host='127.0.0.1', port=27017)
db = client['ArticalRecommend']

artical_tag = db.artical_tag.find_one({'tag':[]})
if (not artical_tag):
    print("There is no artical needs cal tags.")
    exit(1)
artical = db.artical.find_one({"_id":ObjectId(artical_tag['a_id'])})
file_name = "../data_spider/html/" + artical['title_hash'] + ".html"
content = open(file_name, 'rb').read().decode("utf-8")
content = removeLabel(content)
content = jiebacut(content)
content = removeStopWords(content)
content = "".join(content)

tags = jieba.analyse.extract_tags(content, topK=topK)
print(artical['title'])
print(",".join(tags))

artical_tag['tag'] = tags
db.artical_tag.save(artical_tag)
exit(0)
