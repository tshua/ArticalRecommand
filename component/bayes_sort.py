#!/usr/bin/python
# Filename: bayes_sort.py
# _*_ coding:utf-8 _*_

from numpy import *
import re
import random
import pymongo
from bson import ObjectId
import jieba
import sys

def fetchArticalTrain(db): # 获取训练文章
    artical_tag = db.artical_tag.find_one({'catagore':{'$exists':True}, 'is_trained':{'$exists':False}})
    if (not artical_tag):
        exit(1)
    artical = db.artical.find_one({'_id':ObjectId(artical_tag["a_id"])})
    with open("../data_spider/html/" + artical['title_hash'] + ".html", "rb") as f:
        artical_content = f.read().decode("utf-8")
    artical_tag['is_trained'] = 1
    db.artical_tag.save(artical_tag)
    # print(artical_content)
    artical_content = removeLabel(artical_content)
    artical_content = jiebacut(artical_content)
    artical_content = removeStopWords(artical_content)
    return artical_content, artical_tag['catagore']

def fetchArticalClassify(db): # 获取待分类文章
    # artical_tag = db.artical_tag.find_one({'catagore':{'$exists':False}})
    artical_tag = db.artical_tag.find_one({'catagore':{'$exists':True}, 'is_trained':{'$exists':False}})
    if (not artical_tag):
        exit(1)
    artical = db.artical.find_one({'_id':ObjectId(artical_tag["a_id"])})
    with open("../data_spider/html/" + artical['title_hash'] + ".html", "rb") as f:
        artical_content = f.read().decode("utf-8")
    artical_tag['is_trained'] = 1 # 标记完之后就不会拿它去分类了
    db.artical_tag.save(artical_tag)
    # print(artical_content)
    artical_content = removeLabel(artical_content)
    artical_content = jiebacut(artical_content)
    artical_content = removeStopWords(artical_content)
    return artical_content, artical_tag['catagore']

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

def trainBayes(word_list, cata_num, db):
    if (not db.bayes_words.find_one({'cata_num':-1})):
        db.bayes_words.insert({'cata_num':-1, 'total':0})
    item = db.bayes_words.find_one({'cata_num':-1})
    item['total'] += len(word_list)
    db.bayes_words.save(item) # 总词数

    item = db.bayes_words.find_one({'cata_num':cata_num})
    if (not item):
        db.bayes_words.insert({'cata_num':cata_num, 'total':0})
        item = db.bayes_words.find_one({'cata_num':cata_num})
    # print(item['total'])
    # print(len(word_list))
    item['total'] = item['total'] + len(word_list)
    for word in word_list:
        if (word in item):
            item[word] += 1
        else:
            item[word] = 1
    # print(item)
    db.bayes_words.save(item)

def classify(word_list, db):
    total_num = db.bayes_words.find_one({'cata_num':-1})['total']
    cata_total = {}
    for item in db.bayes_words.find({"cata_num":{"$gte":0}},{"total":1, "cata_num":1}):
        cata_total[item['cata_num']] = item['total']

    catagores = []
    for cata in db.catagore.find():
        catagores.append(cata['num'])


    cata_probability = {}
    for word in word_list:
        # 计算这个词一共出现了多少次
        word_num = 0
        for cata in catagores:
            item = db.bayes_words.find_one({"cata_num":cata, word:{'$exists':True}},{word:1, "cata_num":1})
            if (item):
                word_num += item[word]
        for cata in catagores:
            item = db.bayes_words.find_one({"cata_num":cata, word:{'$exists':True}},{word:1, "cata_num":1})
            if (item):
                if (cata in cata_probability):
                    cata_probability[cata] += (item[word]/cata_total[cata]) * (cata_total[cata]/total_num) / (word_num/total_num)
                else:
                    cata_probability[cata] = (item[word]/cata_total[cata]) * (cata_total[cata]/total_num) / (word_num/total_num)

    print(cata_probability)
    max = cata_probability[0]
    res = 0
    for cata in cata_probability:
        if (max < cata_probability[cata]):
            max = cata_probability[cata]
            res = cata
    print(str(res) + "is the max catagore.")
    return res

if __name__ == '__main__':
    client = pymongo.MongoClient(host='127.0.0.1', port=27017)
    db = client['ArticalRecommend']
    if (sys.argv[1] == "train"):
        word_list,cata_num = fetchArticalTrain(db)
        trainBayes(word_list, cata_num, db)
    elif (sys.argv[1] == "classify"):
        word_list,cata_num = fetchArticalClassify(db)
        res = classify(word_list, db)
        if (res == cata_num):
            print("1111")
        else:
            print("2222")
    else:
        print("para error. train/classify")
    exit(0)
