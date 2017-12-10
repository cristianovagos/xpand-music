import json
from urllib.request import urlopen, quote, unquote
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient

# dados de ligação ao GraphDB
ENDPOINT = "http://localhost:7200"
REPO_NAME = "xpand-music"

def getISOCode(country):
    if country == None:
        return

    url = urlopen("https://restcountries.eu/rest/v2/name/" + quote(country))
    data = json.loads(url.read().decode("utf-8"))

    return str(data[0]['alpha2Code']).lower()

def getCountriesGraphDB(num=4):
    client = ApiClient(endpoint=ENDPOINT)
    accessor = GraphDBApi(client)

    query = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX cs: <http://www.xpand.com/rdf/>
                SELECT DISTINCT ?artistCountry
                WHERE{
                    ?artist rdf:type cs:MusicArtist .
                    ?artist cs:country ?artistCountry .
                }
            """

    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query,
                                 repo_name=REPO_NAME)
    res = json.loads(res)

    result = []
    i = 0
    for e in res['results']['bindings']:
        aux = []
        if i >= num:
            break
        aux.append(unquote(e['artistCountry']['value']))
        aux.append(getISOCode(unquote(e['artistCountry']['value'])))
        result.append(aux)
        i += 1
    return result