from datetime import datetime
import re

from tinydb import TinyDB, Query
import requests

from ocd_backend.items import BaseItem
from ocd_backend.utils.misc import parse_date


class BenakiItem(BaseItem):
    override_db = TinyDB('translation-override-db.json')
    cache_db = TinyDB('translation-cache-db.json')
    q = Query()

    session = requests.session()
    translate_url = 'https://translation.googleapis.com/language/translate/v2'

    def _translate(self, text):
        # Skip translation if not requested
        if not 'translate' in self.source_definition:
            return text

        # Use override translation if requested and available
        if 'use_override' in self.source_definition['translate'] and self.source_definition['translate']['use_override'] == True:
            override = self.override_db.search((self.q.source == self.source_definition['translate']['source']) & (self.q.target == self.source_definition['translate']['target']) & (self.q.source_text == text))
            if override:
                return unicode(override[0]['target_text'])

        # Use cached translation if requested and available
        if 'use_cache' in self.source_definition['translate'] and self.source_definition['translate']['use_cache'] == True:
            cache = self.cache_db.search((self.q.source == self.source_definition['translate']['source']) & (self.q.target == self.source_definition['translate']['target']) & (self.q.source_text == text))
            if cache:
                return unicode(cache[0]['target_text'])

        # Else, fetch a new translation for the text and save it in the cache database
        params = {
            'key': self.source_definition['translate']['key'],
            'source': self.source_definition['translate']['source'],
            'target': self.source_definition['translate']['target'],
            'q': text
        }
        target_text = unicode(self.session.get(self.translate_url, params=params).json()['data']['translations'][0]['translatedText'])
        if 'use_cache' in self.source_definition['translate'] and self.source_definition['translate']['use_cache'] == True:
            self.cache_db.insert({
                'source': self.source_definition['translate']['source'],
                'target': self.source_definition['translate']['target'],
                'source_text': text,
                'target_text': target_text

            })
        return unicode(target_text)

    def get_original_object_id(self):
        return unicode(self.original_item['id'].split('/')[-1])

    def get_original_object_urls(self):
        objnr = unicode(self.get_original_object_id())
        return {
                'html': 'http://www.benaki.gr/eMP-Collection/eMuseumPlus?service=ExternalInterface&module=collection&viewType=detailView&objectId=%s' % objnr,
        }

    def get_collection(self):
        return u'Benaki'

    def get_rights(self):
        return unicode(self.original_item['rights'][0])

    def get_combined_index_data(self):
        index_data = {}
        title = unicode(
            self.original_item.get('title', '')[0]
        )
        index_data['title'] = self._translate(title)

        index_data['date_granularity'] = 1
        index_data['date'] = datetime.now()

        index_data['media_urls'] = [
            {
                'original_url': 'http://www.benaki.gr/europeana_images/%s.jpg' % (self.get_original_object_id()),
                'content_type': 'image/jpeg'
            }
        ]

        index_data['all_text'] = self.get_all_text()

        return index_data

    def get_index_data(self):
        index_data = {}
        return index_data

    def get_all_text(self):
        # all text consists of a simple space concatenation of the fields
        fields = [
            'title'
        ]

        text = unicode(self.original_item.get('title', '')[0])
        return unicode(text)
