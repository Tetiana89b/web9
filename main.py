import json

import scrapy
from pymongo import MongoClient
from scrapy.crawler import CrawlerProcess

# Підключення до хмарної бази даних MongoDB
client = MongoClient(
    'mongodb+srv://kara89:321321@cluster0.9wjid2s.mongodb.net/')
db = client['test']
quotes_collection = db['quotes']
authors_collection = db['authors']


class QuotesSpider(scrapy.Spider):
    name = 'quotes'
    start_urls = ['http://quotes.toscrape.com']

    def parse(self, response):
        # Отримання даних про цитати
        quotes = response.css('div.quote')

        authors = {}

        for quote in quotes:
            text = quote.css('span.text::text').get()
            author = quote.css('span small::text').get()
            tags = quote.css('div.tags a.tag::text').getall()

            # Збереження даних про цитати у quotes.json
            with open('quotes.json', 'a', encoding='utf-8') as quotes_file:
                quote_data = {
                    'quote': text,
                    'author': author,
                    'tags': tags
                }
                quotes_file.write(json.dumps(
                    quote_data, ensure_ascii=False) + '\n')

             # Збереження даних про авторів у словник
            if author not in authors:
                authors[author] = {
                    'fullname': author,
                    'born_date': '',
                    'born_location': '',
                    'description': '',
                    'quotes': []
                }
            authors[author]['quotes'].append(text)

        # Збереження даних про авторів у authors.json
        with open('authors.json', 'w', encoding='utf-8') as authors_file:
            authors_data = list(authors.values())
            json.dump(authors_data, authors_file, ensure_ascii=False)

        # Перехід до наступної сторінки
        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)


# Запуск краулера
process = CrawlerProcess()
process.crawl(QuotesSpider)
process.start()
