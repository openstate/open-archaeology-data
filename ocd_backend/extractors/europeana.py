from math import ceil
import json

from ocd_backend.extractors import BaseExtractor, HttpRequestMixin
from ocd_backend.extractors import log
from ocd_backend.exceptions import NotFound


class EuropeanaExtractor(BaseExtractor, HttpRequestMixin):
    api_base_url = 'http://www.europeana.eu/api/v2/search.json'
    items_per_page = 12

    def api_call(self, cursor, params={}):
        params.update(
            wskey=self.source_definition['api_key'],
            query='DATA_PROVIDER%3A%22Benaki+Museum%22',
            cursor=cursor
        )
        url = '%s?wskey=%s&query=%s&cursor=%s' % (self.api_base_url, self.source_definition['api_key'], 'DATA_PROVIDER%3A%22Benaki+Museum%22', cursor)

        log.debug('Getting %s (params: %s)' % (url, params))
        #r = self.http_session.get(url, params=params)
        r = self.http_session.get(url)
        r.raise_for_status()

        return r.json()

    def get_collection_objects(self):
        # Perform an initial call to get the total number of results
        resp = self.api_call('*')
        total_items = resp['totalResults']
        cursor = resp['nextCursor']

        # Calculate the total number of pages that are available
        total_pages = int(ceil(total_items / float(self.items_per_page)))

        log.info('Total collection items to fetch %s (%s pages)',
                 total_items, total_pages)

        for p in xrange(0, total_pages):
            log.info('Getting collection items page %s of %s', p, total_pages)
            resp = self.api_call(cursor)
            cursor = resp['nextCursor']

            for item in resp['items']:
                yield item

    def get_object(self, item):
        log.info('Getting object: %s', item['id'].split('/')[-1])

        return 'application/json', json.dumps(item)

    def run(self):
        if ('api_key' not in self.source_definition or not
                self.source_definition['api_key']):
            raise ValueError('Missing Europeana API key in source settings')

        for item in self.get_collection_objects():
            yield self.get_object(item)
