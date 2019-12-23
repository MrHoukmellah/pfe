import scrapy
import csv
import os
import glob
from openpyxl import Workbook
from scrapy.http import Request
import mysql.connector

from pprint import pprint


def xlsx_writer(csv_content):
    wb = Workbook()
    ws = wb.active

    with open(csv_content, 'r') as f:
        for row in csv.reader(f):
            ws.append(row)

    wb.save(csv_content.replace('.csv', '') + '.xlsx')


def field_validator(field):
    if field:
        field = field
    else:
        field = 'n/a'

    return field


class Jumia2_Spider(scrapy.Spider):
    name = 'Jumia2_spider'
    allowed_domains = ['jumia.ma']
    start_urls = ['https://www.jumia.ma/pc-portables/','https://www.jumia.ma/informatique-ordinateurs-fixes/','https://www.jumia.ma/accessoires-telephone/','https://www.jumia.ma/accessoires-tablettes/','https://www.jumia.ma/telephones-smartphones/','https://www.jumia.ma/tablettes-tactiles/']
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="root",
        database="comparateur"
    )
    
    def start_requests(self):
        urls = {
            'accessoires-telephone': 'https://www.jumia.ma/accessoires-telephone/',
            'accessoires-tablettes': 'https://www.jumia.ma/accessoires-tablettes/',
            'telephones-smartphones': 'https://www.jumia.ma/telephones-smartphones/',
            'tablettes-tactiles': 'https://www.jumia.ma/tablettes-tactiles/',
            'pc-portables' :'https://www.jumia.ma/pc-portables/',
            'ordinateurs-fixes': 'https://www.jumia.ma/informatique-ordinateurs-fixes/'
        }

        for category, url in urls.items():
            yield Request(url, callback=self.parse, meta={'category': category})

    def parse(self, response):
        category = response.meta['category']
        phones = response.xpath('//a[@class="link"]/@href').extract()
        for phone in phones:
            yield Request(phone, callback=self.parse_page, meta={'category': category})

       # next page URL
        next_page_url = response.xpath('//a[@title="Suivant"]/@href').extract_first()
        yield Request(next_page_url, meta={'category': category})

    def parse_page(self, response):
        category = response.meta['category']
        title = response.xpath('//h1[@class="title"]/text()').extract_first()
        product_url = response.url
        brand = response.xpath('//div[@class="sub-title"]/a/text()').extract_first()
        price = float(response.xpath('//span[contains(@class, "price")]/span[@dir="ltr"]/@data-price').extract_first())
        rating1 = response.xpath('//div[@class="container"]/i/following-sibling::span/text()').extract_first()
        rating2 = response.xpath('//div[@class="container"]/following-sibling::footer/text()').extract_first()
        rating = rating1 + ': ' + rating2
        rating = rating.replace(',', '.')
        image_urls = response.xpath('//div[@id="thumbs-slide"]/a/@href').extract()
        description = response.css('.product-description').extract()
        details = response.css('.product-details').extract()

        # Validate fields
        title = field_validator(title)
        product_url = field_validator(product_url)
        brand = field_validator(brand)
        price = field_validator(price)
        rating = field_validator(rating)
        image_urls = field_validator(image_urls)
        description = field_validator(description)
        details = field_validator(details)

        store_id = 1

        cursor = self.db.cursor()

        cursor.execute("SELECT id FROM categories WHERE slug='%s'" % (category))
        result = cursor.fetchone()
        category_id = result[0]

        sql = "INSERT INTO products (title, description, price, rating, url, category_id, store_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        val = (title, description[0], price, rating, product_url, category_id, store_id)
        cursor.execute(sql, val)

        self.db.commit()

        product_id = cursor.lastrowid

        print("=======")
        print(product_id)

        for url in image_urls:
            sql = "INSERT INTO images (url, product_id) VALUES (%s, %s)"
            val = (url, product_id)
            cursor.execute(sql, val)
        
        self.db.commit()

        yield {
            'title': title,
            'category': category,
            'product_url': product_url,
            'brand': brand,
            'price': price,
            'rating': rating,
            'image_urls': image_urls,
            'description': description,
            'details': details
        }

    def close(self, reason):
        # select csv file
        csv_file = max(glob.iglob('data2.csv'), key=os.path.getctime)

        # create xlsx file from csv file
        xlsx_writer(csv_file)