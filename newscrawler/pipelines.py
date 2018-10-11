# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

# used to write to file as unicode encoded file
import codecs
# the datetime is imported so we can convert string to date
# without the conversion we cannot do the comparison between
# two dates
from datetime import datetime
# import json so we can save it to the files
import json
# import os utilites, we use them to manipulate filepath
import os

class NewsPipeline(object):
    '''
    NewsPipeline is the filtering and transforming object.
    It helps to normalize the articles before we store them in
    the JSON files on the disk.
    '''

    def __init__(self):
        '''
        Initialization function.
        Called once when the NewsPipeline is created.
        '''
        # used to count how mane articles we already processed
        self.item_news_counter = 0

    def open_spider(self, spider):
        '''
        when crawling spider is opened set dates we used to filter the articles
        '''
        self.start_date = datetime.strptime(
            spider.settings['START_DATE'],
            '%d.%m.%Y'
        )
        self.stop_date = datetime.strptime(
            spider.settings['STOP_DATE'],
            '%d.%m.%Y'
        )

    def transform_item(self, item):
        '''
        transform text date to date format
        and merge the article list to one text
        '''
        keywords = item['keywords'].split(',')
        item['keywords'] = keywords
        # replace . by _ for more compatibility when saving to file
        item['server'] = item['server'].replace('.', '_')

        return item

    def filter_item_by_date(self, item):
        '''
        filter_item_by_date is used to remove all articles
        that does not belong to our specified 2 moth period

        when the article fits the defined range it is returned
        otherwise none is returned

        the date range is defined in setting.py by START_DATE and STOP_DATE
        '''
        if self.start_date <= item['date'] and item['date'] <= self.stop_date:
            return item

        return

    def process_item(self, item, spider):
        '''
        processing the item is used to transform the fields that are the same
        across the news servers
        the articles are also filtered by the defined range
        '''

        if item is None:
            return None

        processed_item = self.transform_item(item)
        processed_item = self.filter_item_by_date(processed_item)

        # another item processed, increment the counter
        self.item_news_counter += 1

        return processed_item


class JsonPipeline(object):
    '''
    NewsPipeline is the filtering and transforming object.
    It helps to normalize the articles before we store them in
    the JSON files on the disk.
    '''

    def __init__(self):
        '''
        Initialization function.
        Called once when the NewsPipeline is created.
        '''
        # used to count how mane articles we already processed
        self.item_news_counter = 0

    @staticmethod
    def _serialize(o):
        if isinstance(o, datetime):
            return str(o)

    def process_item(self, item, spider):
        '''
        save processed items to the json file
        '''
        if item is None:
            return

        filename = os.path.join('data', item['server'] + str(self.item_news_counter) + '.json')
        data = json.dumps(dict(item), default=JsonPipeline._serialize, ensure_ascii=False)

        with codecs.open(filename, 'w', encoding='utf-8') as file:
            file.write(data)

        # another item processed, increment the counter
        self.item_news_counter += 1

        return item


class ElectionPipeline(object):
    '''
    ElectionPipeline filter out every news
    that is not linked to the elecetions.

    The filtering is based on dictionary match
    '''

    # keywords used to choose whether the news is
    # about elections or not
    # keyword should be selected to match broader
    # terms eg:
    #   draho => drahose, drahosu, drahosovo, ...
    filtering_keywords = [
        'Drahos',
        'Drahoš',
        'Zeman',
        'Fischer',
        'Hannig',
        'Hilšer',
        'Hilser',
        'Horáček',
        'Horacek',
        'Hynek',
        'Kulhánek',
        'Kulhanek',
        'Topolanek',
        'Topolánek'
    ]

    def __init__(self):
        self.item_news_counter = 0

    def process_item(self, item, spider):
        if item is None:
            return None

        for keyword in item['keywords']:
            l_keyword = keyword.lower()
            for filter_keyword in self.filtering_keywords:
                l_filter_keyword = filter_keyword.lower()
                if l_keyword.count(l_filter_keyword) > 0:
                    return item

        # nothing was found
        return None
