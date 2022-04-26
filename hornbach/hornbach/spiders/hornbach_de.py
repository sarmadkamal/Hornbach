import scrapy
from scrapy.http import Response, Request
import regex as re
from bs4 import BeautifulSoup as bs
from math import ceil
from ..items import HornbachItem
import json
import jmespath


class HornbachDeSpider(scrapy.Spider):
    name = 'hornbach.de'
    allowed_domains = ['hornbach.de']
    start_urls = ['http://hornbach.de/']

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "X-Requested-With": "XMLHttpRequest",
        "X-KL-Ajax-Request": "Ajax_Request",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    }

    def start_requests(self):
        url = 'https://www.obi.de/search/grohe/'
        yield Request(url=url, headers=self.headers, callback=self.pagination)

    def pagination(self, response: Response):
        totalRecords = re.findall(r'[\d]+', response.xpath("//div[@class='h-inline']/span//text()").get())[0]
        self.logger.info(f"Total Records found {totalRecords}")
        soup = bs(response.text, features='lxml')
        totalListings = len(soup.findAll('li', class_='product large'))
        for i in range(1, ceil(totalRecords / totalListings) + 1):
            url = f"https://www.obi.de/search/grohe/?page={i}"
            yield Request(url=url, headers=self.headers, callback=self.get_listings)

    def get_listings(self, response: Response):
        soup = bs(response.text, features='lxml')
        listings = soup.findAll('li', class_='product large')
        for listing in listings:
            url = str('https://www.obi.de' + listing.find('a').get('href'))
            yield Request(url=url, headers=self.headers, callback=self.get_pageInfo)

    def get_pageInfo(self, response: Response):

        soup = bs(response.text, features='lxml')
        item = HornbachItem()
