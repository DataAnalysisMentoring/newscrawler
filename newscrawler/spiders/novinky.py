import scrapy
from scrapy import Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from datetime import datetime
from datetime import timedelta

# import our news article item
from newscrawler.items import NewsItem

class NovinkySpider(scrapy.Spider):
    '''
    IhnedSpider is the crawler that crawl thourgh the ihned.cz wesite
    and downloads the articles defined by the rules.

    The server local data is cleaned (converted) here.
    The local data is the date and article format.
    '''

    name = 'novinky'
    allowed_domains = ['novinky.cz']

    # article_link_extrator describes how
    # links to articles look like and extracts them
    article_link_extractor = LinkExtractor(
        allow=('novinky.cz/domaci',),
        restrict_css=('#sectionBox',)
    )

    def __init__(self, *args, **kwargs):
        '''
        __init__ is initialization method
        it is called first time when the class
        is created
        '''

        # setup the url generator
        self.url = self.nextUrl()

        # call setup of the parent class
        super().__init__(*args, **kwargs)

    def nextUrl(self):
        '''
        nextUrl generates the url for archive of novinky.cz
        it generates the url to match our defined date range

        This method is a python generator. Basicaly it is a
        cycle which can be paused. It remembers it state
        and returns new generated value everytime it is
        called.
        '''

        # current date for which this method generates the url
        # starting date is START_DATE from settings
        currentDate = datetime.strptime(
            self.settings.get('START_DATE'),
            '%d.%m.%Y'
        )

        # end date where this generator stop generating urls
        endDate = datetime.strptime(
            self.settings.get('STOP_DATE'),
            '%d.%m.%Y'
        )

        # delta is the amount of days this method add
        # everytime it is called
        delta = timedelta(days=1)

        while currentDate <= endDate:
            # generate novinky.cz url for the archive
            # {} is replaced with formatted date stored in currentDate
            self.current_date = currentDate
            yield 'https://www.novinky.cz/archiv?id=8&date={}'.format(currentDate.strftime('%d.%m.%Y'))
            currentDate += delta

    def start_requests(self):
        ## grab the first URL to being crawling
        start_url = next(self.url)

        request = Request(start_url, dont_filter=True)

        yield request

    def parse(self, response):
        '''
        parse has the logic fro crawling the novinky.cz
        This site is different so we need custom logic
        '''

        # get the links for all articles on the page
        links = self.article_link_extractor.extract_links(response)
        for link in links:
            yield Request(link.url, callback=self.parse_item)

        # go to the next date for more articles
        yield Request(next(self.url))

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
        article['title'] = response.css('h1::text').extract()[0]
        article['date'] = self.current_date
        found_article = response.css('#contentArticleBox p::text').extract()
        article['article'] = self.transform_article(found_article)
        article['keywords'] = response.css('meta[name=keywords]::attr(content)').extract()[0]
        article['server'] = 'novinky.cz'

        return article
