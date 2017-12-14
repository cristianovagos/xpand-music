import json, xml.etree.ElementTree as ET
from urllib.request import urlopen, unquote, quote
from ..urls import getTopArtistsURL
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient

# dados de ligação ao GraphDB
ENDPOINT = "http://localhost:7200"
REPO_NAME = "xpand-music"

def getTopArtists(num=5, page=1):
    file = urlopen(getTopArtistsURL(num, page))
    tree = ET.parse(file)
    root = tree.getroot()
    result = []

    for x in root.findall('artists/artist'):
        aux = []
        aux.append(str(x.find('name').text))
        aux.append(x.find('image[@size="extralarge"]').text)
        result.append(aux)
    return result

def getTopArtistsGraphDB(num=5, page=1):
    client = ApiClient(endpoint=ENDPOINT)
    accessor = GraphDBApi(client)

    query = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX cs: <http://www.xpand.com/rdf/>
                PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                SELECT ?artistName ?artistCover ?artistPlayCount
                WHERE{
                    ?artist rdf:type cs:MusicArtist .
                    ?artist foaf:name ?artistName .
                    ?artist foaf:Image ?artistCover .
                    ?artist cs:playCount ?artistPlayCount .
                }
                ORDER BY DESC(xsd:integer(?artistPlayCount))
            """

    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query,
                                 repo_name=REPO_NAME)
    res = json.loads(res)

    result = []
    i = 0
    for e in res['results']['bindings']:
        aux = []
        aux.append(unquote(e['artistName']['value']))
        aux.append(e['artistCover']['value'])
        result.append(aux)
        i += 1

    result = result[(page - 1) * num:(page * num)]
    return result

def getTopArtistsCountriesGraphDB(country, num=4, page=1):
    client = ApiClient(endpoint=ENDPOINT)
    accessor = GraphDBApi(client)

    query = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX cs: <http://www.xpand.com/rdf/>
                PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                SELECT ?artistName ?artistCover ?artistPlayCount
                WHERE{
                    ?artist rdf:type cs:MusicArtist .
                    ?artist foaf:name ?artistName .
                    ?artist foaf:Image ?artistCover .
                    ?artist cs:playCount ?artistPlayCount .
                    ?artist cs:country "%s" .
                }
                ORDER BY DESC(xsd:integer(?artistPlayCount))
            """ % (quote(country))

    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query,
                                 repo_name=REPO_NAME)
    res = json.loads(res)

    result = []
    i = 0
    for e in res['results']['bindings']:
        if i >= num:
            break
        aux = {}
        aux['name'] = unquote(e['artistName']['value'])
        aux['image'] = e['artistCover']['value']
        aux['country'] = country
        result.append(aux)
        i += 1
    return result
