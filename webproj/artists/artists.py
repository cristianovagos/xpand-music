import xml.etree.ElementTree as ET
from urllib.request import urlopen

def getTOPArtistsURL():
    return urlopen("http://ws.audioscrobbler.com/2.0/?method=chart.gettopartists&api_key=32f8947b156b3993b3ff9159b81f4667")

def getTOPArtists(num=5):
    allArtists = getTOPArtistsURL()
    tree = ET.parse(allArtists)
    root = tree.getroot()

    resultArtists = []
    i = 0
    for artist in root.findall('artists'):
        for prop in artist.findall('artist'):
            if i >= 3:
                break
            artistArr = []
            artistArr.append(prop.find('name').text)
            artistArr.append(prop.find('.//image[@size="medium"]').text)
            artistArr.append(prop.find('playcount').text)
            resultArtists.append(artistArr)
            i+=1

    return resultArtists
