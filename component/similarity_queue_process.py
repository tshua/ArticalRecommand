#!/usr/bin/python
# Filename: similarity_queue_process.py
# _*_ coding:utf-8 _*_

# 利用余弦相似度算法计算文本相似度

import pymongo
from numpy import *
import re
import pymongo
from bson import ObjectId
import jieba

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


def createVocabList(dataSet):  # 创建词库 这里就是直接把所有词去重后，当作词库
    vocabSet = set([])
    for document in dataSet:
        vocabSet = vocabSet | set(document)
    return list(vocabSet)


def setOfWords2Vec(vocabList, inputSet):  # 文本词向量。词库中每个词当作一个特征，文本中就该词，该词特征就是1，没有就是0
    returnVec = [0] * len(vocabList)
    for word in inputSet:
        if word in vocabList:
            returnVec[vocabList.index(word)] += 1
        else:
            print("the word: %s is not in my Vocabulary!" % word)
    return returnVec


client = pymongo.MongoClient(host='127.0.0.1', port=27017)
db = client['ArticalRecommend']

artical_pair = db.similar_queue.find_one({'is_processed':{'$exists':False}})
if (not artical_pair):
    print("there is no artical pair limit to process.")
    exit(1)

artical_pair['is_processed'] = 1
db.similar_queue.save(artical_pair)

artical1 = db.artical.find_one({'_id':ObjectId(artical_pair['a_id1'])})
artical2 = db.artical.find_one({'_id':ObjectId(artical_pair['a_id2'])})

file_name = "../data_spider/html/" + artical1['title_hash'] + ".html"
content1 = open(file_name, 'rb').read().decode("utf-8")
content1 = removeLabel(content1)
content1 = jiebacut(content1)
content1 = removeStopWords(content1)

file_name = "../data_spider/html/" + artical2['title_hash'] + ".html"
content2 = open(file_name, 'rb').read().decode("utf-8")
content2 = removeLabel(content2)
content2 = jiebacut(content2)
content2 = removeStopWords(content2)

tmp = content1
tmp.extend(content2)
vocabList = createVocabList(tmp)

vec1 = setOfWords2Vec(vocabList, content1)
vec2 = setOfWords2Vec(vocabList, content2)

result1 = 0.0
result2 = 0.0
result3 = 0.0
for i in range(len(vec1)):
    result1 += vec1[i] * vec2[i]  # sum(X*Y)
    result2 += vec1[i] ** 2  # sum(X*X)
    result3 += vec2[i] ** 2  # sum(Y*Y)
cos_val = result1/((result2*result3)**0.5)

print(str(cos_val))

if (cos_val > 0.5): # 夹角<30度
    artical_tag1 = db.artical_tag.find_one({'a_id':artical_pair['a_id1']})
    artical_tag2 = db.artical_tag.find_one({'a_id':artical_pair['a_id2']})

    if 'similar_aids' in artical1:
        artical_tag1['similar_aids'] = artical_tag1['similar_aids'].append(artical_pair['a_id2'])
    else:
        artical_tag1['similar_aids'] = [artical_pair['a_id2']]

    if 'similar_aids' in artical2:
        artical_tag2['similar_aids'] = artical_tag2['similar_aids'].append(artical_pair['a_id1'])
    else:
        artical_tag2['similar_aids'] = [artical_pair['a_id1']]

exit(0)