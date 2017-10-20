import xml.etree.ElementTree as ET
from urllib.request import urlopen
from ..urls import getTopArtistsURL

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


