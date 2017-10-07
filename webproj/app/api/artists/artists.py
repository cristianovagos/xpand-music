import xml.etree.ElementTree as ET
from urllib.request import urlopen

from webproj.app.api.albums.albums import getTopAlbums
from webproj.app.api.tracks.tracks import getTopTracks
from webproj.app.api.urls import getTopArtistsURL, getArtistInfoURL


def getArtistInfo(artist, numAlbums=5, numTracks=5):
    artistURL = urlopen( str(getArtistInfoURL(artist)) )
    tree = ET.parse(artistURL)
    root = tree.getroot()

    resultArtist = []
    similarArtists = []
    biography = []
    for x in root.findall('artist'):
        biography.append(x.find('bio/summary').text)
        biography.append(x.find('bio/content').text)
        biography.append(x.find('.//image[@size="mega"]').text)
        biography.append(x.find('name').text)
        for y in x.findall('similar/artist'):
            similar = []
            similar.append(y.find('name').text)
            similar.append(y.find('.//image[@size="mega"]').text)
            similarArtists.append(similar)

    topAlbums = getTopAlbums(artist)
    topXAlbums = topAlbums[:numAlbums]

    topTracks = getTopTracks(artist)
    topXTracks = topTracks[:numTracks]

    resultArtist.append(biography)
    resultArtist.append(similarArtists)
    resultArtist.append(topAlbums)
    resultArtist.append(topXAlbums)
    resultArtist.append(topTracks)
    resultArtist.append(topXTracks)

    return resultArtist

def getTopArtists(num=5):
    allArtists = urlopen( str(getTopArtistsURL()) )
    tree = ET.parse(allArtists)
    root = tree.getroot()

    resultArtists = []
    i = 0
    for artist in root.findall('artists'):
        for prop in artist.findall('artist'):
            if i >= num:
                break
            artistArr = []
            artistArr.append(prop.find('name').text)
            artistArr.append(prop.find('.//image[@size="medium"]').text)
            artistArr.append(prop.find('playcount').text)
            resultArtists.append(artistArr)
            i+=1

    return resultArtists
