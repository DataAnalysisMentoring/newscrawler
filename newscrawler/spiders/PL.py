# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from datetime import datetime

# import our news article item
from newscrawler.items import NewsItem

class PLSpider(CrawlSpider):
    '''
    PLSpider is the crawler that crawl thourgh the www.parlamentnilisty.cz wesite
    and downloads the articles defined by the rules.

    The server local data is cleaned (converted) here.
    The local data is the date and article format.
    '''

    name = 'PL'
    allowed_domains = ['parlamentnilisty.cz']

    # the url from which we download the articles
    # we define only one URL because the articles
    # are located usualy only on one URL
    start_urls = ['https://www.parlamentnilisty.cz/zpravy']

    # rules define how the crawles get the article links
    # and search for next link
    rules = (
        # extract the links to articles
        # allow defines search pattern repeating in the article links
        # restrict_css defines in which element we are looking for
        # the links
        Rule(
            LinkExtractor(
                allow=('/.*/.*/.*',),
                restrict_css=('.articles-list',)
            ),
            callback='parse_item',
        ),

        # urls for next page
        # works the same as previous
        Rule(
            LinkExtractor(
                allow=('zpravy\?p=',),
                restrict_css=('.pagination',)
            )
        ),
    )

    def transform_date(self, date):
        '''
        transorm the date from the article
        '''
        return datetime.strptime(date.strip(), '%d. %m. %Y %H:%M')

    def transform_article(self, article):
        '''
        tranform how the article is converted from site specific format
        to our unified article format: one long text
        '''
        return ' '.join(article)

    def transform_keywords(self, keywords):
        return ', '.join(keywords)

    def parse_item(self, response):
        '''
        parse the data from website
        create new NewsItem and then fills it by the crawler
        '''
        # create new article from our defined item
        article = NewsItem()
        print(response.url)
        # parse the data from the website
        article['title'] = response.css('section.article-header h1::text').extract()[0]
        date = response.css('div.time::text').extract()[0]
        article['date'] = self.transform_date(date)
        found_article = response.css('section.article-content p::text').extract()
        article['article'] = self.transform_article(found_article)
        keywords = response.css('section.article-tags a::text').extract()
        article['keywords'] = self.transform_keywords(keywords)
        article['server'] = 'parlamentnilisty.cz'

        return article
