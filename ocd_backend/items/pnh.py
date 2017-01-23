from datetime import datetime
from ocd_backend.items import BaseItem

class PnhItem(BaseItem):
    
    cache_str = '&cache=yes'
    
    namespaces = {
        'oai': 'http://www.openarchives.org/OAI/2.0/',
        'dc': 'http://purl.org/dc/elements/1.1/',
        'dcterms' : 'http://purl.org/dc/terms/'
    }
        
    media_mime_types = {
        'png': 'image/png',
        'jpg': 'image/jpeg'
    }

    def _get_text_or_none(self, xpath_expression):
        node = self.original_item.find(xpath_expression, namespaces=self.namespaces)
        if node is not None and node.text.strip() is not None:
            return unicode(node.text).strip()

        return None

    def get_original_object_id(self):
        return self._get_text_or_none('.//oai:header/oai:identifier').strip()
    
    def get_original_object_urls(self):
        original_id = self.get_original_object_id()
        return {
            'html': self._get_text_or_none('.//oai:metadata/oai:deeplinkpubl'),
            'xml': '%s?verb=GetRecord&identifier=%s&metadataPrefix=%s' % (self.source_definition['oai_base_url'], original_id, self.source_definition['oai_metadata_prefix'])
        }
       
    def get_rights(self):
        rights = self._get_text_or_none('.//oai:metadata/oai:dc_rights')
        if rights:
            return rights
        return u'Licentie PNH ontbreekt' 
        
    def get_collection(self):
        dc_type = self._get_text_or_none('.//oai:metadata/oai:dc_type')
        if dc_type:
            return dc_type
        return u'Collectienaam PNH ontbreekt'

    def _get_clean_link(self, text):
        if text.endswith(self.cache_str):
            return text.replace(self.cache_str, '')
        else: 
            return text
    
    def _get_clean_date(self, date):         
        date = date.replace('-', ' ')
        date_arr = date.split(' ')
        for ele in date_arr:
            try:
                cdate = int(ele)
            except:
                continue            
            cgran = 6
            return cdate, cgran
        
        return None , None
    
    def get_combined_index_data(self):
        combined_index_data = {}
        
        title = self._get_text_or_none('.//oai:title')
        combined_index_data['title'] = title

        description = self._get_text_or_none('.//dc:description[@language="DUT"]')
        if description:
            combined_index_data['description'] = description

        date = self._get_text_or_none('.//dcterms:temporal')
        
        if date:
            cdate , cgran = self._get_clean_date(date)
            if cdate and cgran:
                combined_index_data['date'] = datetime(cdate, 1, 1)
                combined_index_data['date_granularity'] = cgran
                   
        # No authors for archaeology
        combined_index_data['authors'] = []

        # Media 
        mediums = self.original_item.findall(
            './/oai:europeana_isshownby',
            namespaces=self.namespaces
        )

        if mediums is not None:
            combined_index_data['media_urls'] = []

            for medium in mediums:
                combined_index_data['media_urls'].append({
                    'original_url': medium.text.strip(),
                    'content_type': 
                        self.media_mime_types[
                            self._get_clean_link(
                                medium.text.strip()
                            ).split('.')[-1].lower()
                        ]
                })

        return combined_index_data

    def get_index_data(self):
        return {}
   
    def get_all_text(self):
        text_items = []

        # Title
        text_items.append(self._get_text_or_none('.//oai:title'))

        # Alternative title
        text_items.append(self._get_text_or_none('.//dc:title'))
        
        # Creators
        creators = self.original_item.findall('.//oai:dc_creator',
                                              namespaces=self.namespaces)
        for creator in creators:
            text_items.append(unicode(creator.text))

        # Subject
        text_items.append(self._get_text_or_none('.//dc:subject'))
       
        # Description
        text_items.append(self._get_text_or_none('.//dc:description[@language="DUT"]'))

        # Identifier
        text_items.append(self._get_text_or_none('.//oai:identifier').strip())

        # Source
        #text_items.append(self._get_text_or_none('.//oi:source[@xml:lang="nl"]'))

        # Spatial
        text_items.append(self._get_text_or_none('.//oai:vindplaats'))
        
        text_items.append(self._get_text_or_none('.//oai:objecttype'))
        
        text_items.append(self._get_text_or_none('.//oai:europeana_country'))
        
        text_items.append(self._get_text_or_none('.//oai:archisnummer'))

        text_items.append(self._get_text_or_none('.//oai:tentoonstellingsgeschiedenis'))
        
        items = self.original_item.findall('.//oai:thesperiode',
                                              namespaces=self.namespaces)
        for item in items:
            text_items.append(unicode(item.text))

        text_items.append(self._get_text_or_none('.//oai:objectid'))

        items = self.original_item.findall('.//oai:periodezoeken',
                                              namespaces=self.namespaces)
        for item in items:
            text_items.append(unicode(item.text))

        text_items.append(self._get_text_or_none('.//oai:standplaatsextern'))

        text_items.append(self._get_text_or_none('.//oai:Standplaats'))

        text_items.append(self._get_text_or_none('.//oai:sitestatus'))

        items = self.original_item.findall('.//oai:thesvondst',
                                              namespaces=self.namespaces)
        for item in items:
            text_items.append(unicode(item.text))

        items = self.original_item.findall('.//oai:publieksinformatie',
                                              namespaces=self.namespaces)
        for item in items:
            text_items.append(unicode(item.text))

        text_items.append(self._get_text_or_none('.//oai:rubriek'))

        text_items.append(self._get_text_or_none('.//oai:sitename'))

        items = self.original_item.findall('.//oai:literatuur',
                                              namespaces=self.namespaces)
        for item in items:
            text_items.append(unicode(item.text))

        items = self.original_item.findall('.//dcterms:temporal',
                                              namespaces=self.namespaces)
        for item in items:
            text_items.append(unicode(item.text))

        text_items.append(self._get_text_or_none('.//oai:thescultuur'))

        text_items.append(self._get_text_or_none('.//oai:dcterms_medium'))

        text_items.append(self._get_text_or_none('.//oai:thesgeomorfologie'))

        text_items.append(self._get_text_or_none('.//oai:thescomplex'))

        text_items.append(self._get_text_or_none('.//oai:inscribed'))

        items = self.original_item.findall('.//dcterms:spatial',
                                              namespaces=self.namespaces)
        for item in items:
            text_items.append(unicode(item.text))

        text_items.append(self._get_text_or_none('.//oai:markings'))

        return u' '.join([ti for ti in text_items if ti is not None])
