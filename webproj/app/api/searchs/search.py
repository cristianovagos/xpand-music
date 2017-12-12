from ..urls import getArtistSearchURL, getAlbumSearchURL
from urllib.request import urlopen
import xml.etree.ElementTree as ET

def searchArtist(artistSearch):
    url = getArtistSearchURL(artistSearch, 12, 1)
    file = urlopen(url)

    straux = str(file.read().decode())
    juntar = '<results for="' + artistSearch + '" xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">'
    straux = straux.replace('<results for="' + artistSearch + '">', juntar)

    root = ET.fromstring(straux)
    result = []

    for x in root.findall('results/artistmatches/artist'):
        aux = {}
        aux['name'] = x.find('name').text
        aux['image'] = x.find('image[@size="extralarge"]').text
        if aux['image'] == None:
            aux['image'] = "https://www.shareicon.net/data/2015/07/09/66681_music_512x512.png"
        result.append(aux)
    return result

def searchAlbum(albumSearch):
    url = getAlbumSearchURL(albumSearch, 12, 1)
    file = urlopen(url)

    straux = str(file.read().decode())
    juntar = '<results for="' + albumSearch + '" xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">'
    straux = straux.replace('<results for="' + albumSearch + '">', juntar)

    root = ET.fromstring(straux)
    result = []

    for x in root.findall('results/albummatches/album'):
        aux = {}
        aux['name'] = x.find('name').text
        aux['artist'] = x.find('artist').text
        aux['image'] = x.find('image[@size="extralarge"]').text
        if aux['image'] == None:
            aux['image'] = "https://www.shareicon.net/data/2015/07/09/66681_music_512x512.png"
        result.append(aux)
    return result

