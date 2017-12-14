import json, xml.etree.ElementTree as ET
from urllib.request import urlopen, unquote
from ..urls import getTopTracksURL
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient

# dados de ligação ao GraphDB
ENDPOINT = "http://localhost:7200"
REPO_NAME = "xpand-music"

def getTopTracks(num=5, page=1):
    file = urlopen(getTopTracksURL(num, page))
    tree = ET.parse(file)
    root = tree.getroot()
    result = []

    for x in root.findall('tracks/track'):
        aux = []
        aux.append(str(x.find('artist/name').text))
        aux.append(str(x.find('name').text))
        aux.append(x.find('image[@size="extralarge"]').text)
        result.append(aux)
    return result

def getTopTracksGraphDB(num=5, page=1):
    client = ApiClient(endpoint=ENDPOINT)
    accessor = GraphDBApi(client)

    query = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX cs: <http://www.xpand.com/rdf/>
                PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                SELECT ?artistName ?albumCover ?trackName ?youtubeID
                WHERE{
                    ?track rdf:type cs:Track .
                    ?track foaf:name ?trackName .
                    ?track cs:playCount ?trackPlayCount .
                    ?track cs:Album ?trackAlbum .
                    ?track cs:MusicArtist ?artist .
                    ?artist foaf:name ?artistName .
                    ?trackAlbum foaf:Image ?albumCover .
                    OPTIONAL {
                        ?track cs:youtubeVideo ?youtubeID .
                    }
                }
                ORDER BY DESC(xsd:integer(?trackPlayCount))
            """

    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query,
                                 repo_name=REPO_NAME)
    res = json.loads(res)

    result = []
    i = 0
    for e in res['results']['bindings']:
        if i >= (num*page):
            break
        if i < ((num*page) - num):
            continue

        aux = []
        aux.append(unquote(e['artistName']['value']))
        aux.append(unquote(e['trackName']['value']))
        aux.append(e['albumCover']['value'])
        try:
            aux.append(unquote(e['youtubeID']['value']))
        except Exception:
            aux.append(None)
        result.append(aux)
        i += 1

    return result