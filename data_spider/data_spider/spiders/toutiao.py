#!/usr/bin/python
# Filename : toutiao.py

import scrapy
from data_spider.items import ToutiaoItem
from scrapy.selector import Selector
import json
import time
import data_spider.common
import re


class TouTiaoSpider(scrapy.Spider):
    name = 'toutiao'
    allowed_domains = ["toutiao.com"]
    base_category_url = 'http://www.toutiao.com/api/pc/feed/?category={0}&utm_source=toutiao&widen=1&max_behot_time={1}&max_behot_time_tmp={2}&tadrequire=true&as=A115681FDC5A156&cp=58FCFA5125769E1'
    catagorys = ['news_society', 'news_society', 'news_entertainment', 'news_tech', 'news_sports', 'news_car',
                  'news_finance', 'funny', 'news_military', 'news_world', 'news_fashion',
                  'news_travel', 'news_discovery', 'news_baby', 'news_regimen', 'news_story', 'news_essay', 'news_game',
                  'news_history', 'news_food']
    # 社会 娱乐 科技 体育 汽车 财经 搞笑 更多 军事 国际 时尚 旅游 探索 育儿 养生 故事 美文 游戏 历史 美食
    #catagorys = ['news_society']

    current_time = int(time.time())
    start_urls = []
    for catagory in catagorys:
        for i in range(0, 6 * 2):# 1小时1次 # 12 * 6 * 2):  # 0 点一次 12点一次
            start_urls.append(base_category_url.format(catagory, current_time - 300 * i, current_time - 300 * i))

    base_url = 'http://toutiao.com'


    def parse(self, response):
        '''获取ajax传来的list,并生成文章的url'''
        body = response.body.decode('utf-8')
        articals = json.loads(body)
        for artical in articals['data']:
            if ('group' in artical['source_url']):  # 过滤广告
                toutiaoItem = ToutiaoItem()
                toutiaoItem['title'] = artical['title']
                url = self.base_url + artical['source_url']
                toutiaoItem['image_url'] = '#'  # '#'代表没有缩略图
                if ('image_list' in artical.keys()):
                    for image in artical['image_list']:     # 只要一张图片,省事
                        toutiaoItem['image_url'] = str(image)
                        break
                toutiaoItem['source_url'] = url
                toutiaoItem['catagore'] = artical['chinese_tag']
                self.writeToTmpFile(toutiaoItem)
                time.sleep(0.3)
                yield scrapy.Request(url, self.parseSourceUrl)

    def parseSourceUrl(self, response):
        '''解析文章 发送items给pipeline'''
        article_content = response.xpath("//div [@id='article-main']").extract()
        if (article_content):
            toutiaoItem = ToutiaoItem()
            toutiaoItem['title'] = \
                Selector(text=article_content[0]).xpath('//h1 [@class="article-title"]/text()').extract()[0]
            toutiaoItem['source'] = '头条'
            toutiaoItem['tag'] = Selector(text=article_content[0]).xpath('//li [@class="label-item"]/text()').extract()
            toutiaoItem['title_hash'] = data_spider.common.get_md5_value(toutiaoItem['title'].encode("utf-8"))
            toutiaoItem['artical_url'] = str(toutiaoItem['title_hash']) + ".html"
            article_time = Selector(text=article_content[0]).xpath('//span [@class="time"]/text()').extract()
            toutiaoItem['artical_time'] = ''
            if (article_time):
                toutiaoItem['artical_time'] = article_time[0]
            toutiaoItem['collect_time'] = int(time.time())
            article_content, number  =  re.subn(r"href=\".*\"", '', article_content[0])
            article_content = bytes(article_content, "utf-8")
            with open("./html/" + toutiaoItem['artical_url'], 'wb') as f:
                f.write(article_content)
            yield toutiaoItem

    def writeToTmpFile(self, item):
        '''把list信息写入临时文件'''
        arr = [ item['title'], item['image_url'], item['source_url'], item['catagore'] ]
        line =  '|'.join(arr)
        line += "\n"
        line = bytes(line,'utf-8')
        with open('tmp_imageurl.txt', 'ab') as f:
            f.writelines([line])