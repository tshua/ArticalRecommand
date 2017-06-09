#!/bin/bash

rm tmp_imageurl.txt
rm tmp_imageurl
scrapy crawl toutiao > log 2>&1
echo 'scrapy down'
sort tmp_imageurl.txt | uniq > tmp_imageurl
python data_spider/scripts/ImageUrl_Process.py
echo 'image_url process done'
