import xml.etree.ElementTree as ET
from urllib.request import urlopen
from ..urls import getArtistTopAlbumsURL

def getTopAlbums(artist):
    file = urlopen( getArtistTopAlbumsURL(artist, limit=6) )
    tree = ET.parse(file)
    root = tree.getroot()
    result = []

    for x in root.findall('topalbums/album'):
        aux = []
        aux.append(str(x.find('name').text))
        aux.append(x.find('image[@size="extralarge"]').text)
        result.append(aux)

    print(result)
    return result


