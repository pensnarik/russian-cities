#!/usr/bin/env python3

# Russian cities parser

# Script gets list of the Russian cities from Wikipedia and basic information
# about them: name, subject, district, population and coordinates.
# Copyright Andrey Zhidenkov, 2018 (c)

import os
import sys
import json

from lxml.html import fromstring

from parselab.parsing import BasicParser
from parselab.network import NetworkManager
from parselab.cache import FileCache

class App(BasicParser):

    data = list()

    def __init__(self):
        self.cache = FileCache(namespace='russian-cities', path=os.environ.get('CACHE_PATH'))
        self.net = NetworkManager()

    def get_coords(self, url):
        page = self.get_page(url)
        html = fromstring(page)

        try:
            span = html.xpath('//span[contains(@class, "coordinates")]//a[@class="mw-kartographer-maplink"]')[0]
        except IndexError:
            return {'lat': '', 'lon': ''}

        return {'lat': span.get('data-lat'), 'lon': span.get('data-lon')}

    def run(self):
        page = self.get_page('https://ru.wikipedia.org/wiki/Список_городов_России')
        html = fromstring(page)

        for tr in html.xpath('//table/tbody/tr'):
            columns = tr.xpath('.//td')
            if len(columns) != 7:
                continue
            name = columns[2].xpath('./a')[0].text_content().strip()
            url = columns[2].xpath('./a')[0].get('href')
            subject = columns[3].text_content().strip()
            district = columns[4].text_content().strip()
            population = int(columns[5].get('data-sort-value'))

            city = {'name': name, 'subject': subject, 'district': district, 'population': population}
            city.update({'coords': self.get_coords('https://ru.wikipedia.org%s' % url)})
            self.data.append(city)

            print(name, file=sys.stderr)
        output = sorted(self.data, key=lambda k: k['name'])
        print(json.dumps(output, ensure_ascii=False, sort_keys=True))

if __name__ == '__main__':
    app = App()
    sys.exit(app.run())
