import xml.etree.ElementTree as ET
from urllib.request import urlopen
from webproj.app.api.urls import getTopTracksURL

def getTopTracks(artista):
    file = urlopen( getTopTracksURL() )
    tree = ET.parse(file)
    root = tree.getroot()
    result = []

    for x in root.findall('toptracks/track'):
        aux = []
        aux.append(x.find('name').text)
        aux.append(x.find('image[@size="extralarge"]').text)
        result.append(aux)

    return result