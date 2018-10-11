# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from datetime import datetime

# import our news article item
from newscrawler.items import NewsItem

class IhnedSpider(CrawlSpider):
    '''
    IhnedSpider is the crawler that crawl thourgh the ihned.cz wesite
    and downloads the articles defined by the rules.

    The server local data is cleaned (converted) here.
    The local data is the date and article format.
    '''

    name = 'idnes.cz'
    allowed_domains = ['idnes.cz']

    # the url from which we download the articles
    # we define only one URL because the articles
    # are located usualy only on one URL
    start_urls = ['https://ostrava.idnes.cz/']

    # rules define how the crawles get the article links
    # and search for next link
    rules = (
        # extract the links to articles
        # allow defines search pattern repeating in the article links
        # restrict_css defines in which element we are looking for
        # the links
        Rule(
            LinkExtractor(
                allow=('ostrava.idnes.cz/',),
                restrict_css=('.art-full',)
            ),
            callback='parse_item',
        ),

        # urls for next page
        # works the same as previous
        Rule(
            LinkExtractor(
                allow=('.col-a',),
                restrict_css=('.tac',)
            )
        ),
    )

    def transform_date(self, date):
        '''
        transorm the date from the article
        '''
        return datetime.strptime(date.strip(), '%d. %m. %Y')

    def transform_article(self, article):
        '''
        tranform how the article is converted from site specific format
        to our unified article format: one long text
        '''
        return ' '.join(article)

    def parse_item(self, response):
        '''
        parse the data from website
        create new NewsItem and then fills it by the crawler
        '''
        # create new article from our defined item
        article = NewsItem()

        # parse the data from the website
        article['title'] = response.css('h1.title:og:title').extract()[0]
        date = response.css('div.counters:article:published_time').extract()[0]
        article['date'] = self.transform_date(date)
        found_article = response.css('div.bbtext p::text').extract()
        article['article'] = self.transform_article(found_article)
        article['keywords'] = response.css('meta[name=keywords]::attr(content)').extract()[0]
        article['server'] = 'idnes.cz'

        return article
