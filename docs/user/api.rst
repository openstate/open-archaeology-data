.. _restapi:

RESTful API
===========

.. warning::

   This page currently shows a draft of the API specification. **The format of some of the request/response pairs is still subject to change!**

General notes
-------------

The API accepts requests with JSON content and returns JSON data in all of its responses (unless stated otherwise). Standard HTTP response codes are used to indicate errors. In case of an error, a more detailed description can be found in the JSON response body. UTF-8 character encoding is used in both requests and responses.

All API URLs referenced in this documentation start with the either of the following base parts, depending on if you want the original Dutch or translated English data (translated using Google Translate):

- :rest_api_nl_v0:`v0`
- :rest_api_en_v0:`v0`

All API endpoints are designed according to the idea that there is an operation within a *context*: methods on the "root" context are executed across all datasets; :ref:`/search <rest_search>` executes a search across all collections, whereas :ref:`/pnh/search <rest_source_search>` executes a search on the Provincie Noord-Holland collection.

Arguments to an endpoint are placed behind the method definition, or supplied as JSON in a POST request. For instance, the :ref:`similar objects endpoint <rest_similar>` can be executed within the context of a collection, and needs an ``object_id`` to execute on.

Collection overview and statistics
----------------------------------

.. http:get:: /sources

   Get a list of all available sources (collections) with item counts

   **Example request**

   .. sourcecode:: http

      $ curl -i -XGET 'http://api-en.archaeologydata.com/v0/sources'

   **Example response**

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Server: nginx/1.11.5
      Date: Wed, 25 Jan 2017 08:29:36 GMT
      Content-Type: application/json
      Content-Length: 207
      Connection: keep-alive
      Access-Control-Allow-Origin: *

      {
        "sources": [
          {
            "count": 18585,
            "id": "pzh",
            "name": "Collectienaam PZH ontbreekt"
          },
          {
            "count": 10799,
            "id": "pnh",
            "name": "NH Collectie"
          }
        ]
      }

   :statuscode 200: OK, no errors.

.. _rest_search:

Searching within multiple collections
-------------------------------------

.. http:post:: /search

   Search for objects through all indexed datasets.

   **Example request**

   .. sourcecode:: http

      $ curl -i -XPOST 'http://api-en.archaeologydata.com/v0/search' -d '{
         "query": "glass",
         "facets": {
            "collection": {},
            "date": {"interval": "day"}
         },
         "filters": {
            "media_content_type": {"terms": ["image/jpeg", "video/webm"]}
         },
         "size": 1
      }'

   **Example response** (limited facets to 6 results for readability)

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Server: nginx/1.11.5
      Date: Wed, 25 Jan 2017 08:30:56 GMT
      Content-Type: application/json
      Content-Length: 6630
      Connection: keep-alive
      Vary: Accept-Encoding
      Access-Control-Allow-Origin: *

      {
        "facets": {
          "collection": {
            "_type": "terms",
            "missing": 0,
            "other": 0,
            "terms": [
              {
                "count": 364,
                "term": "NH Collectie"
              },
              {
                "count": 127,
                "term": "Collectienaam PZH ontbreekt"
              }
            ],
            "total": 491
          },
          "date": {
            "_type": "date_histogram",
            "entries": [
              {
                "count": 4,
                "time": -60904915200000
              },
              {
                "count": 2,
                "time": -60589296000000
              },
              {
                "count": 3,
                "time": -59958144000000
              },
			  ...
              {
                "count": 1,
                "time": -2240524800000
              },
              {
                "count": 4,
                "time": -2208988800000
              },
              {
                "count": 1,
                "time": -1262304000000
              }
            ]
          }
        },
        "hits": {
          "hits": [
            {
              "_id": "6a69f592b04f6d1b75ff97f6b824359711ad1b5f",
              "_score": 2.6290884,
              "_source": {
                "description": "Glass; blue; millefiori glass; fragment",
                "enrichments": {
                  "media_urls": [
                    {
                      "content_type": "image/jpeg",
                      "image_format": "JPEG",
                      "image_mode": "RGB",
                      "media_type": "image",
                      "original_url": "http://collectie.huisvanhilde.nl/cc/imageproxy.aspx?server=10.0.10.211&port=17502&filename=images62/Velsen/Westerwijk_1966/Objecten/10291-11(1).jpg&cache=yes",
                      "resolution": {
                        "height": 3110,
                        "total_pixels": 9690760,
                        "width": 3116
                      },
                      "size_in_bytes": 880955,
                      "url": "http://api-en.archaeologydata.com/v0/resolve/273014d0f2d9e79a9ac8b12598830918c46c1e2f"
                    }
                  ]
                },
                "media_urls": [
                  {
                    "content_type": "image/jpeg",
                    "url": "http://api-en.archaeologydata.com/v0/resolve/273014d0f2d9e79a9ac8b12598830918c46c1e2f"
                  }
                ],
                "meta": {
                  "collection": "NH Collectie",
                  "oad_url": "http://c-oad-app-en:5000/v0/pnh/6a69f592b04f6d1b75ff97f6b824359711ad1b5f",
                  "original_object_id": "10291-11",
                  "original_object_urls": {
                    "html": "http://collectie.huisvanhilde.nl/?query=Records/relatedid=[Object56134]&label=Zoekopdracht&showtype=record",
                    "xml": "http://62.221.199.184:17518/oai?verb=GetRecord&identifier=10291-11&metadataPrefix=oai_pnh"
                  },
                  "processing_finished": "2017-01-25T02:47:17.737953",
                  "processing_started": "2017-01-25T00:06:13.099970",
                  "rights": "Naamsvermelding-NietCommercieel-GeenAfgeleideWerken 3.0 Nederland (CC BY-NC-ND 3.0) \nhttp://creativecommons.org/licenses/by-nc-nd/3.0/nl/",
                  "source_id": "pnh"
                },
                "title": "Glass"
              }
            }
          ],
          "max_score": 2.6290884,
          "total": 491
        },
        "took": 15
      }

   **Query**

   Besides standard keyword searches, a basic query syntax is supported. This syntax supports the following special characters:

   - ``+`` signifies an AND operation

   - ``|`` signifies an OR operation
   - ``-`` negates a single token
   - ``"`` wraps a number of tokens to signify a phrase for searching
   - ``*`` at the end of a term signifies a prefix query
   - ``(`` and ``)`` signify precedence

   The default strategy is to perform an AND query.

   **Facets**

   The ``facets`` object determines which facets should be returned. The keys of this object should contain the names of a the requested facets, the values should be objects. These objects are used to set per facet options. Facet defaults will be used when the options dictionary is empty.

   To specify the number of facet values that should be returned (for term based facets):

   .. sourcecode:: javascript

      {
         "media_content_type": {"count": 100}
      }

   For a date based facet the 'bucket size' of the histogram can be specified:

   .. sourcecode:: javascript

      {
         "date": {"interval": "year"}
      }

   Allowed sizes are ``year``, ``quarter``, ``month``, ``week`` and ``day`` (the default size is ``month``).

   **Filters**

   Results can be filtered on one or more properties. Each key of the ``filters`` object represents a filter, the values should be objects. When filtering on multiple fields only documents that match all filters are included in the result set. The names of the filters match those of the facets.

   For example, to retrieve documents that have media associated with them of the type ``image/jpeg`` **or** ``image/png``:

   .. sourcecode:: javascript

      {
         "media_content_type": {
            "terms": ['image/jpeg', 'image/png']
         }
      }

   Use the following format to filter on a date range:

   .. sourcecode:: javascript

      {
         "date": {
            "from": "2011-12-24",
            "to": "2011-12-28"
         }
      }

   :jsonparameter query: one or more keywords.
   :jsonparameter filters: an object with field and values to filter on (optional).
   :jsonparameter facets: an object with fields for which to return facets (optional).
   :jsonparameter sort: the field the search results are sorted on. By default, results are sorted by relevancy to the query.
   :jsonparameter size: the maximum number of documents to return (optional, defaults to 10).
   :jsonparameter from: the offset from the first result (optional, defaults to 0).
   :statuscode 200: OK, no errors.
   :statuscode 400: Bad Request. An accompanying error message will explain why the request was invalid.

.. _rest_source_search:

Searching within a single collection
------------------------------------

.. http:post:: /(source_id)/search

   Search for objects within a specific dataset. The objects returned by this method will also include fields that are specific to the queried dataset, rather than only those fields that all indexed datasets have in common.

   See specifications of the :ref:`search method <rest_search>` for the request and response format.

   :jsonparameter query: one or more keywords.
   :jsonparameter filters: an object with field and values to filter on (optional).
   :jsonparameter facets: an object with fields for which to return facets (optional).
   :jsonparameter sort: the field the search results are sorted on. By default, results are sorted by relevancy to the query.
   :jsonparameter size: the maximum number of documents to return (optional, defaults to 10).
   :jsonparameter from: the offset from the first result (optional, defaults to 0).
   :statuscode 200: OK, no errors.
   :statuscode 400: Bad Request. An accompanying error message will explain why the request was invalid.
   :statuscode 404: The requested source does not exist.

.. _rest_get:

Retrieving a single object
--------------------------

.. http:get:: /(source_id)/(object_id)

   Retrieve the contents of a single object.

   **Example request**

   .. sourcecode:: http

      $ curl -i 'http://api-en.archaeologydata.com/v0/pnh/701287f9d6d4bf1727e3569b5aebb8d65ce13163'

   **Example response**

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Server: nginx/1.11.5
      Date: Wed, 25 Jan 2017 10:53:13 GMT
      Content-Type: application/json
      Content-Length: 1709
      Connection: keep-alive
      Vary: Accept-Encoding
      Access-Control-Allow-Origin: *

      {
        "date": "1400-01-01T00:00:00",
        "date_granularity": 6,
        "description": "Dagger; fe-dollar-; Quillon dagger; triangular, narrowed angel and wooden opschuifheft.",
        "enrichments": {
          "media_urls": [
            {
              "content_type": "image/jpeg",
              "image_format": "JPEG",
              "image_mode": "RGB",
              "media_type": "image",
              "original_url": "http://collectie.huisvanhilde.nl/cc/imageproxy.aspx?server=10.0.10.211&port=17502&filename=images59/Bergen/Egmond/Egmond aan den Hoef/Kasteel/doosnummers-objecten-ladenkast metaal/5002-081.jpg&cache=yes",
              "resolution": {
                "height": 600,
                "total_pixels": 360000,
                "width": 600
              },
              "size_in_bytes": 17574,
              "url": "http://api-en.archaeologydata.com/v0/resolve/9807ddf0789c15e71fe259df46e4e3801c0a12c5"
            }
          ]
        },
        "media_urls": [
          {
            "content_type": "image/jpeg",
            "url": "http://api-en.archaeologydata.com/v0/resolve/9807ddf0789c15e71fe259df46e4e3801c0a12c5"
          }
        ],
        "meta": {
          "collection": "NH Collectie",
          "original_object_id": "5002-081",
          "original_object_urls": {
            "html": "http://collectie.huisvanhilde.nl/?query=Records/relatedid=[Object38791]&label=Zoekopdracht&showtype=record",
            "xml": "http://62.221.199.184:17518/oai?verb=GetRecord&identifier=5002-081&metadataPrefix=oai_pnh"
          },
          "processing_finished": "2017-01-25T02:47:23.384497",
          "processing_started": "2017-01-25T00:33:41.614905",
          "rights": "Naamsvermelding-NietCommercieel-GeenAfgeleideWerken 3.0 Nederland (CC BY-NC-ND 3.0) \nhttp://creativecommons.org/licenses/by-nc-nd/3.0/nl/",
          "source_id": "pnh"
        },
        "title": "Dagger"
      }

   :statuscode 200: OK, no errors.
   :statuscode 404: The source and/or object does not exist.

.. http:get:: /(source_id)/(object_id)/source

   Retrieves the object's data in its original and unmodified form, as used as input for the Open Archaeology Data extractor(s). Being able to retrieve the object in it's original form can be useful for debugging purposes (i.e. when fields are missing or odd values are returned in the OAD representation of the object).

   The value of the ``Content-Type`` response header depends on the type of data that is returned by the data provider.

   **Example request**

   .. sourcecode:: http

      $ curl -i 'http://api-en.archaeologydata.com/v0/pnh/701287f9d6d4bf1727e3569b5aebb8d65ce13163/source'

   **Example response**

   .. sourcecode:: http

      <record xmlns="http://www.openarchives.org/OAI/2.0/" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <header>
          <identifier>5002-081                                  </identifier>
          <datestamp>2016-02-11T13:52:21Z</datestamp>
        </header>
        <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:edm="http://www.europeana.eu/schemas/edm/" xmlns:wgs84_pos="http://www.w3.org/2003/01/geo/wgs84_pos#" xmlns:foaf="http://xmlns.com/foaf/0.1/" xmlns:rdaGr2="http://rdvocab.info/ElementsGr2/" xmlns:oai="http://www.openarchives.org/OAI/2.0/" xmlns:owl="http://www.w3.org/2002/07/owl#" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:ore="http://www.openarchives.org/ore/terms/" xmlns:skos="http://www.w3.org/2004/02/skos/core#" xmlns:dcterms="http://purl.org/dc/terms/">
          <dc:identifier>5002-081                                  </dc:identifier>
          <relatedid>Object38791</relatedid>
          <recordtype>Object</recordtype>
          <title>Dolk</title>
          <dc:title>Dolk (onderdeel)</dc:title>
          <dc:subject>Dolk (onderdeel)</dc:subject>
          <dc:description language="DUT">Dolk; fe-dol-; Quillon dagger; driekantig, versmalde angel en houten opschuifheft.</dc:description>
          <dc_type>NH Collectie</dc_type>
          <europeana_type>DIVERS</europeana_type>
          <dc_source>The Museum System</dc_source>
          <dcterms:temporal>1400-1500</dcterms:temporal>
          <dcterms:spatial>Middeleeuwen laat: 1050 - 1500 nC</dcterms:spatial>
          <dcterms:spatial>Middeleeuwen: 450 - 1500 nC</dcterms:spatial>
          <dcterms:spatial>Middeleeuwen laat B: 1250 - 1500 nC</dcterms:spatial>
          <dcterms:temporal>1400-1500</dcterms:temporal>
          <dc_creator ConstituentID="3279" DisplayOrder="2" Role="Uitvoerder onderzoek" creatorandrole="PWN Waterleidingbedrijf Noord-Holland (Uitvoerder onderzoek)">PWN Waterleidingbedrijf Noord-Holland</dc_creator>
          <dc_creator ConstituentID="3176" DisplayOrder="1" Role="Uitvoerder onderzoek" creatorandrole="Rijksmuseum van Oudheden (Uitvoerder onderzoek)">Rijksmuseum van Oudheden</dc_creator>
          <dc_rights>Naamsvermelding-NietCommercieel-GeenAfgeleideWerken 3.0 Nederland (CC BY-NC-ND 3.0)
http  ://creativecommons.org/licenses/by-nc-nd/3.0/nl/</dc_rights>
          <dc_format>3.1/30.5/-</dc_format>
          <dc_language>DUT</dc_language>
          <europeana_language>DUT</europeana_language>
          <dcterms_medium>IJzer; koperlegering; hout</dcterms_medium>
          <europeana_country>The Netherlands</europeana_country>
          <europeana_provider>Provincie Noord-Holland</europeana_provider>
          <europeana_isshownby>http://collectie.huisvanhilde.nl/cc/imageproxy.aspx?server=10.0.10.211&amp;port=17502&amp;filename=images59/Bergen/Egmond/Egmond aan den Hoef/Kasteel/doosnummers-objecten-ladenkast metaal/5002-081.jpg&amp;cache=yes</europeana_isshownby>
          <europeana_uri>http://collectie.huisvanhilde.nl</europeana_uri>
          <objectid>38791</objectid>
          <periodezoeken>Middeleeuwen laat: 1050 - 1500 nC</periodezoeken>
          <periodezoeken>Middeleeuwen: 450 - 1500 nC</periodezoeken>
          <periodezoeken>Middeleeuwen laat B: 1250 - 1500 nC</periodezoeken>
          <thesperiode>Middeleeuwen laat: 1050 - 1500 nC</thesperiode>
          <thesperiode>Middeleeuwen: 450 - 1500 nC</thesperiode>
          <thesperiode>Middeleeuwen laat B: 1250 - 1500 nC</thesperiode>
          <thesvondst>Dolk (onderdeel)</thesvondst>
          <thesvondst>IJzer</thesvondst>
          <thesvondst>Metaalsoorten</thesvondst>
          <objecttype>object</objecttype>
          <vindplaats regio="Kennemerland" gemeente="Bergen" plaats="Egmond aan den Hoef" jaar="1932-1935" vindplaatstotaal="Slot op den Hoef, Egmond aan den Hoef, Bergen" googleurl="http://www.google.com/maps/place/Nederland, Egmond aan den Hoef" googleplace="Nederland, Egmond aan den Hoef">Slot op den Hoef</vindplaats>
          <rubriek>Composiet</rubriek>
          <relobjectsites sitename="Slot op den Hoef" deeplinksitepubl="http://collectie.huisvanhilde.nl/?query=Records/relatedid=[Site203]&amp;label=Zoekopdracht&amp;showtype=record">Site203</relobjectsites>
          <relobjectconst dc_creator="PWN Waterleidingbedrijf Noord-Holland">Constituent3279</relobjectconst>
          <relobjectconst dc_creator="Rijksmuseum van Oudheden">Constituent3176</relobjectconst>
          <Standplaats>Depot C</Standplaats>
          <publiek>1</publiek>
          <deeplinkpubl>http://collectie.huisvanhilde.nl/?query=Records/relatedid=[Object38791]&amp;label=Zoekopdracht&amp;showtype=record</deeplinkpubl>
          <relatedid>Object38791</relatedid>
          <vindplaats xco="105.400" yco="515.150">Slot op den Hoef</vindplaats>
        </metadata>
      </record>

   :statuscode 200: OK, no errors.
   :statuscode 404: The requested source and/or object does not exist.

.. _rest_similar:

Similar items
-------------

.. http:post:: /similar/(object_id)

  Retrieve objects similar to the object with id ``object_id`` across all indexed datasets (i.e. it could return similarly described pieces of glass from different collection). From the contents of the object, the most descriptive terms ("descriptive" here means the terms with the highest tf-idf value in the document) are used to search across collections.

  As a search is executed, the response format is exactly the same as the response returned by the :ref:`search endpoint <rest_search>`. The request format is almost the same, with the exception that a query can't be specified (as the document with id ``object_id`` is considered the query). That means that faceting, filtering and sorting on the resulting set are fully supported.

  **Example request**

  .. sourcecode:: http

    $ curl -i -XPOST 'http://api-en.archaeologydata.com/v0/similar/<object_id>' -d '{
       "facets": {
          "collection": {},
          "date": {"interval": "day"}
       },
       "filters": {
          "media_content_type": {"terms": ["image/jpeg", "video/webm"]}
       },
       "size": 10,
       "from": 30,
       "sort": "date"
    }'

  :jsonparameter filters: an object with field and values to filter on (optional).
  :jsonparameter facets: an object with fields for which to return facets (optional).
  :jsonparameter sort: the field the search results are sorted on. By default, results are sorted by relevancy to the query.
  :jsonparameter size: the maximum number of documents to return (optional, defaults to 10).
  :jsonparameter from: the offset from the first result (optional, defaults to 0).
  :statuscode 200: OK, no errors.
  :statuscode 400: Bad Request. An accompanying error message will explain why the request was invalid.


.. http:post:: /(source_id)/similar/(object_id)

  Retrieve objects similar to the object with id ``object_id`` from the dataset specified by ``source_id``. You can find similar objects in the same collection, or objects in a different collection that are similar to the provided object.

  :jsonparameter filters: an object with field and values to filter on (optional).
  :jsonparameter facets: an object with fields for which to return facets (optional).
  :jsonparameter sort: the field the search results are sorted on. By default, results are sorted by relevancy to the query.
  :jsonparameter size: the maximum number of documents to return (optional, defaults to 10).
  :jsonparameter from: the offset from the first result (optional, defaults to 0).
  :statuscode 200: OK, no errors.
  :statuscode 400: Bad Request. An accompanying error message will explain why the request was invalid.

.. _rest_resolver:

Resolver
--------
The Open Archaeology Data API provides all (media) urls as Open Archaeology Data Resolver URLs. This will route all requests for content through the API, which will process and validate the URL, and provide a redirect to the original content source. This will allow for caching or rate limiting on API level in the future, to precent excessive amounts of requests to the sources.

.. http:get:: /resolve/(url_hash)

  Resolves the provided URL, and redirects the request with a 302 if it is valid. If it is not, a 404 is returned. Depending on the Accept header in the request, it returns a JSON-encoded response detailing what went wrong, or a HTML-page, allowing for transparent use in websites.

  Additionally, the resolver provides an thumbnailing service as well. By supplying a ``size`` parameter to the requested resolver, the user can obtain a thumbnailed version of the media item, if it is an image. Currently, we support images where the mimetype of the original image is ``image/jpeg``, ``image/png`` or ``image/tiff``. The API will return a thumbnail from a cache if the image has been requested before, or generate and cache it if it has not.

  When successfully requesting a thumbnail, the resolver will return a ``302`` redirect to the cached version of the image. This will considerably speed up the retrieval of images (as some sources do not have the resources to serve their content in a web environment). Also, developers are **strongly** encouraged to use the resolver url of an image over the ``Location`` returned by the server, as that value may change over time (we may move the images to another physical location, change the URL, or use a different caching system. The resolve URL ensures that API users are always redirected to the proper location.

  The API currently provides the following formats:

  * **large**: 1000px; the image will be either 1000px high or wide, depending on the orientation of the image (i.e. *portrait* will be 1000px high, whereas *landscape* will be 1000px wide.
  * **medium**: 500px; the image will be either 1000px high or wide, depending on the orientation of the image (i.e. *portrait* will be 500px high, whereas *landscape* will be 500px wide.
  * **small**: 250px; the image will be either 1000px high or wide, depending on the orientation of the image (i.e. *portrait* will be 250px high, whereas *landscape* will be 250px wide.
  * **large_sq**: 1000x1000px; the image will be cropped from the center to be 1000x1000px
  * **medium_sq**: 500x500px; the image will be cropped from the center to be 500x500px
  * **small_sq**: 250x250px; the image will be cropped from the center to be 250x250px

    **Example json request**

    .. sourcecode:: http

      $ curl -i -Haccept:application/json -XGET http://api-en.archaeologydata.com/v0/resolve/<url_hash>

    **Example browser-like request**

    .. sourcecode:: http

      $ curl -i -Haccept:text/html -XGET http://api-en.archaeologydata.com/v0/resolve/<url_hash>

    **Example thumbnail json request**

    .. sourcecode:: http

      $ curl -i -Haccept:application/json -XGET http://api-en.archaeologydata.com/v0/resolve/<url_hash>?size=medium_sq

    **Example success response**

    .. sourcecode:: http

      HTTP/1.0 302 Found
      Location: http://example.com/example.jpg

    .. sourcecode:: http

      HTTP/1.0 302 FOUND
      Location: http://<STATIC_SUB_DOMAIN>.archaeologydata.com/media/<img_name>.jpg"

    **Example failed json response**

    .. sourcecode:: http

      HTTP/1.0 404 NOT FOUND
      Content-Type: application/json
      Content-Length: 98
      Date: Sat, 24 May 2014 14:33:00 GMT

      {
        "error": "URL is not available; the source may no longer be available",
        "status": "error"
      }

    **Example failed HTML response**

    .. sourcecode:: http

      HTTP/1.0 404 NOT FOUND
      Content-Type: text/html; charset=utf-8
      Content-Length: 123
      Date: Sat, 24 May 2014 14:32:37 GMT

      <html>
        <body>
          There is no original url available. You may have an outdated URL, or the resolve id is incorrect.
        </body>
      </html>
