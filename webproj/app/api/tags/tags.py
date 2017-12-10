import json, xml.etree.ElementTree as ET
from urllib.request import urlopen, unquote, quote
from ..urls import getTagTopArtistsURL, getTopTagsURL
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient

# dados de ligação ao GraphDB
ENDPOINT = "http://localhost:7200"
REPO_NAME = "xpand-music"

def getTagTopArtists(tag, num=4):
    file = urlopen(getTagTopArtistsURL(tag))
    tree = ET.parse(file)
    root = tree.getroot()
    result = []
    i=0
    for x in root.findall('topartists/artist'):
        if i >= num:
            break
        aux = {}
        aux['name'] = str(x.find('name').text)
        aux['image'] = str(x.find('image[@size="extralarge"]').text)
        aux['tag'] =  str(tag)
        result.append(aux)
        i+=1
    return result


def topTags():
    file = urlopen(getTopTagsURL(limit=10))
    tree = ET.parse(file)
    root = tree.getroot()
    result = []

    for x in root.findall('tags/tag'):
        result.append(str(x.find('name').text))

    return result


def getTopTagsGraphDB(num=4):
    client = ApiClient(endpoint=ENDPOINT)
    accessor = GraphDBApi(client)

    query = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX cs: <http://www.xpand.com/rdf/>
                PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                SELECT ?tagName
                WHERE{
                    ?tag rdf:type cs:Tag .
                    ?tag foaf:name ?tagName .
                    ?tag cs:playCount ?tagPlayCount .
                }
                ORDER BY DESC(xsd:integer(?tagPlayCount))
            """

    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query,
                                 repo_name=REPO_NAME)
    res = json.loads(res)

    result = []
    i = 0
    for e in res['results']['bindings']:
        if i >= num:
            break
        result.append(unquote(e['tagName']['value']))
        i += 1
    return result

def getTagTopArtistsGraphDB(tag, num=4):
    client = ApiClient(endpoint=ENDPOINT)
    accessor = GraphDBApi(client)

    query = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX cs: <http://www.xpand.com/rdf/>
                PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                SELECT ?artistName ?artistImage
                WHERE{
                    ?tag rdf:type cs:Tag .
                    ?tag foaf:name "%s" .
                    ?artist rdf:type cs:MusicArtist .
                    ?artist cs:Tag ?tag .
                    ?artist foaf:name ?artistName .
                    ?artist foaf:Image ?artistImage .
                    ?artist cs:playCount ?artistPlayCount
                }
                ORDER BY DESC(xsd:integer(?artistPlayCount))
            """ % (quote(tag))

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
        aux['image'] = e['artistImage']['value']
        aux['tag'] = tag
        result.append(aux)
        i += 1
    return result