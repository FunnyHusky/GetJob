# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

#智联招聘网址的item
class ZhilianzhaopingItem(scrapy.Item):
   zhiwei = scrapy.Field()
   company = scrapy.Field()
   money = scrapy.Field()
   work = scrapy.Field()
	
