# -*- coding: utf-8 -*-
import scrapy


class BoutikaSpider(scrapy.Spider):
    name = 'boutika'
    allowed_domains = ['boutika.co.ma']
    start_urls = ['http://boutika.co.ma/']

    def parse(self, response):
        pass
