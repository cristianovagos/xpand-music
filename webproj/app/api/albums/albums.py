import xml.etree.ElementTree as ET
from urllib.request import urlopen
from webproj.app.api.urls import getTopArtistsURL

def getTopAlbums(artist):
    file = urlopen( getTopArtistsURL() )
    tree = ET.parse(file)
    root = tree.getroot()
    result = []

    for x in root.findall('topalbums/album'):
        aux = []
        aux.append(str(x.find('name').text))
        aux.append(x.find('image[@size="extralarge"]').text)
        result.append(aux)
    return result

