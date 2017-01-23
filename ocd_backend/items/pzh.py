from datetime import datetime
from ocd_backend.items import BaseItem
from tinydb import TinyDB, Query
import io
import requests

class PzhItem(BaseItem):

#### http://archeologie.zuid-holland.nl/oaiinfo.htm
#### http://62.221.199.184:5842/oai?verb=ListRecords&metadataPrefix=studie
#### http://dev.cithosting.nl/pnhpubliek2/cc/imageproxy.aspx?server=10.0.10.211&port=17502&filename=images52/opmeer%2faartswoud%2ft_hoog_drie_bunders_1972_1978%2fobjecten%2f3950-01(6).jpg&bg=F8F8F8&cache=yes&bordercolor=B8B8B8&borderwidth=1&borderheight=1&passepartoutcolor=ffffff&passepartoutwidth=10&passepartoutheight=10

    loc_str = 'Archeologisch Basis Register\\Toponiemenlijst\\'

    namespaces = {
        'oai': 'http://www.openarchives.org/OAI/2.0/',
        'dc': 'http://purl.org/dc/elements/1.1/',
        'dcterms' : 'http://purl.org/dc/terms/'
    }

    media_mime_types = {
        'png': 'image/png',
        'jpg': 'image/jpeg'
    }

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
        #target_text = 'DIT IS EEN TEST'
        if 'use_cache' in self.source_definition['translate'] and self.source_definition['translate']['use_cache'] == True:
            self.cache_db.insert({
                'source': self.source_definition['translate']['source'],
                'target': self.source_definition['translate']['target'],
                'source_text': text,
                'target_text': target_text

            })
        return unicode(target_text)

    def _get_text_or_none(self, xpath_expression):
        node = self.original_item.find(xpath_expression, namespaces=self.namespaces)
        if node is not None and node.text.strip() is not None:
            return unicode(node.text).strip()

        return None

    def get_original_object_id(self):
        return self._get_text_or_none('.//oai:metadata/oai:ID').strip()

    def get_original_object_urls(self):
        original_id = self.get_original_object_id()
        return_data = {
            'xml': '%s?verb=GetRecord&identifier=%s&metadataPrefix=%s' % (self.source_definition['oai_base_url'], original_id, self.source_definition['oai_metadata_prefix'])
        }
        html = self._get_text_or_none('.//oai:metadata/oai:URL')
        if html:
            return_data['html'] = html
        return return_data

    def get_rights(self):
        return u'Licentie PZH ontbreekt'

    def get_collection(self):
        return u'Collectienaam PZH ontbreekt'

    def _get_clean_link(self, text):
        return text.split('?')[0]

    def _process_mediums(self, mediums):
        return_data = []
        if mediums is None:
            return return_data
        else:
            for medium in mediums:
                url = medium.text.strip()
                # Skip if the URL is already present (prevents duplicates)
                if [item for item in return_data if url in item.values()]:
                    continue
                return_data.append({
                    'original_url': url,
                    'content_type': 
                        self.media_mime_types[
                            self._get_clean_link(
                                medium.text
                            ).split('.')[-1].lower()
                        ]
                })
            return return_data


    def get_combined_index_data(self):
        combined_index_data = {}

        title = self._get_text_or_none('.//oai:metadata/oai:Description')
        if title:
            combined_index_data['title'] = self._translate(title)

        items = self.original_item.findall('.//oai:Voorwerp',
                                              namespaces=self.namespaces)
        descriptions = []
        for item in items:
            descriptions.append(self._translate(unicode(item.text)))
        if descriptions:
            combined_index_data['description'] = '. '.join(descriptions)

        date = self._get_text_or_none('.//oai:metadata/oai:Periode_sort')
        if date:
            cdate = int(date.split(';')[1])
            if cdate:
                combined_index_data['date'] = datetime(cdate, 1, 1)
                combined_index_data['date_granularity'] = 1

        # No authors for archaeology
        combined_index_data['authors'] = []

        # Media 
        mediums1 = self.original_item.findall('.//oai:metadata/oai:Image',
            namespaces=self.namespaces)
        mediums2 = self.original_item.findall('.//oai:metadata/oai:OtherImages',
            namespaces=self.namespaces)
        medium_data = []
        medium_data += self._process_mediums(mediums1)
        medium_data += self._process_mediums(mediums2)
        if medium_data:
            combined_index_data['media_urls'] = medium_data
        return combined_index_data

    def get_index_data(self):
        return {}

    def get_all_text(self):
        text_items = []

        # Title
        text_items.append(self._get_text_or_none('.//oai:metadata/oai:Description'))
        text_items.append(self._get_text_or_none('.//oai:metadata/oai:Voorwerp'))

        # Identifier
        text_items.append(self._get_text_or_none('.//oai:metadata/oai:ID'))

        items = self.original_item.findall('.//oai:Locatie',
                                              namespaces=self.namespaces)
        for item in items:
            text_items.append(unicode(item.text))

        items = self.original_item.findall('.//oai:ObjectLevel',
                                              namespaces=self.namespaces)
        for item in items:
            text_items.append(unicode(item.text))

        items = self.original_item.findall('.//oai:Vindplaats',
                                              namespaces=self.namespaces)
        for item in items:
            text_items.append(unicode(item.text))

        return u' '.join([ti for ti in text_items if ti is not None])
