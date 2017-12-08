import json
from urllib.request import urlopen, quote

def getISOCode(country):
    if country == None:
        return

    url = urlopen("https://restcountries.eu/rest/v2/name/" + quote(country))
    data = json.loads(url.read().decode("utf-8"))

    return str(data[0]['alpha2Code']).lower()
