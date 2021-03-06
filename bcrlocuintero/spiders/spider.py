import json

import scrapy

from scrapy.loader import ItemLoader

from ..items import BcrlocuinteroItem
from itemloaders.processors import TakeFirst

import requests

url = "https://www.bcrlocuinte.ro/bin/erstegroup/gemesgapi/feature/gem_site_ro_www-bcrlocuinte-ro-ro-es7/,"

base_payload = "{\"filter\":[{\"key\":\"path\",\"value\":\"/content/sites/ro/bcr/www_bcrlocuinte_ro/ro/presa\"}]," \
             "\"page\":%s,\"query\":\"*\",\"items\":10,\"sort\":\"DATE_RELEVANCE\",\"requiredFields\":[{\"fields\":[" \
             "\"teasers.NEWS_DEFAULT\",\"teasers.NEWS_ARCHIVE\",\"teasers.newsArchive\"]}]} "
headers = {
  'Connection': 'keep-alive',
  'Pragma': 'no-cache',
  'Cache-Control': 'no-cache',
  'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
  'sec-ch-ua-mobile': '?0',
  'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36',
  'Content-Type': 'application/json',
  'Accept': '*/*',
  'Origin': 'https://www.bcrlocuinte.ro',
  'Sec-Fetch-Site': 'same-origin',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Dest': 'empty',
  'Referer': 'https://www.bcrlocuinte.ro/ro/presa',
  'Accept-Language': 'en-US,en;q=0.9,bg;q=0.8',
  'Cookie': 'TCPID=121321418811564566500; _ga=GA1.2.207346627.1614687489; TC_PRIVACY=0@002@21%2C22@20@1614687490572@; TC_PRIVACY_CENTER=21%2C22; _gid=GA1.2.1877931582.1615451368; 3cf5c10c8e62ed6f6f7394262fadd5c2=ffb311b6d6c2f7e071b7c1a53fef5c06'
}


class BcrlocuinteroSpider(scrapy.Spider):
	name = 'bcrlocuintero'
	start_urls = ['https://www.bcrlocuinte.ro/ro/presa']
	page = 0

	def parse(self, response):
		payload = base_payload % self.page
		data = requests.request("POST", url, headers=headers, data=payload)
		raw_data = json.loads(data.text)
		for post in raw_data['hits']['hits']:
			link = post['_source']['url']
			date = post['_source']['date']
			title = post['_source']['title']
			yield response.follow(link, self.parse_post, cb_kwargs={'date': date, 'title': title})
		if self.page < raw_data['hits']['total'] // 10:
			self.page += 1
			yield response.follow(response.url, self.parse, dont_filter=True)

	def parse_post(self, response, date, title):
		description = response.xpath(
			'//div[@class="w-auto mw-full rte"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=BcrlocuinteroItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
