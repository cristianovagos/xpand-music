import xml.etree.ElementTree as ET
from urllib.request import urlopen
from ..urls import getTopTracksURL

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
