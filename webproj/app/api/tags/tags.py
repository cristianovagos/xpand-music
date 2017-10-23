import xml.etree.ElementTree as ET
from urllib.request import urlopen
from ..urls import getTagTopArtistsURL, getTopTagsURL
from ...model.artist import Artist

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
    print(tag + ':')
    print(result)
    return result


def topTags():
    file = urlopen(getTopTagsURL(limit=10))
    tree = ET.parse(file)
    root = tree.getroot()
    result = []

    for x in root.findall('tags/tag'):
        result.append(str(x.find('name').text))

    return result