import scrapy
import csv
import os
import glob
from openpyxl import Workbook
from scrapy.http import Request

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


class Jumia_Spider(scrapy.Spider):
    name = 'Jumia_spider'
    allowed_domains = ['jumia.ma']
    start_urls = ['https://www.jumia.ma/ordinateurs-pc/']

    def parse(self, response):
        ordinateurs = response.xpath('//a[@class="link"]/@href').extract()
        for ordinateur in ordinateurs:
            yield Request(ordinateur, callback=self.parse_page)

       # next page URL
        next_page_url = response.xpath(
             '//a[@title="Suivant"]/@href').extract_first()
        yield Request(next_page_url)

    def parse_page(self, response):
        title = response.xpath('//h1[@class="title"]/text()').extract_first()
        product_url = response.url
        brand = response.xpath(
            '//div[@class="sub-title"]/a/text()').extract_first()
        price = '#' + response.xpath(
            '//span[contains(@class, "price")]/span[@dir="ltr"]/@data-price'
        ).extract_first()
        rating1 = response.xpath(
            '//div[@class="container"]/i/following-sibling::span/text()'
        ).extract_first()
        rating2 = response.xpath(
            '//div[@class="container"]/following-sibling::footer/text()'
        ).extract_first()
        rating = rating1 + ': ' + rating2
        rating = rating.replace(',', '.')
        image_urls = response.xpath(
            '//div[@id="thumbs-slide"]/a/@href').extract()
        description = response.css(
            '.product-description').extract()
        details = response.css(
            '.product-details').extract()
        # Validate fields
        title = field_validator(title)
        product_url = field_validator(product_url)
        brand = field_validator(brand)
        price = field_validator(price)
        rating = field_validator(rating)
        image_urls = field_validator(image_urls)
        description = field_validator(description)
        details = field_validator(details)


        yield {
            'title': title,
            'product_url': product_url,
            'brand': brand,
            'price': price,
            'rating': rating,
            'image_urls': image_urls,
            'description': description,
            'details' : details
        }

    def close(self, reason):
        # select csv file
        csv_file = max(glob.iglob('*.csv'), key=os.path.getctime)

        # create xlsx file from csv file
        xlsx_writer(csv_file)