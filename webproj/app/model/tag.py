import xml.etree.ElementTree as ET
from urllib.parse import quote
from urllib.request import urlopen
from urllib.error import HTTPError
from webproj.app.api.urls import getTagInfoURL, getTagTopAlbumsURL, \
    getTagTopArtistsURL, getTagTopTracksURL

class Tag:

    def __init__(self, name, max_items=5):
        self.name = None
        self.topAlbums = []
        self.topArtists = []
        self.topTracks = []
        self.wikiTextShort = None
        self.wikiTextFull = None

        self.max_items = max_items

        self.fetchInfo()

    def fetchInfo(self):
        try:
            url = urlopen( getTagInfoURL(quote(self.name)) )
        except HTTPError:
            print('Tag doesn\'t exist!')
        else:
            tree = ET.parse(url)
            root = tree.getroot()

            for x in root.findall('tag'):
                self.name = x.find('name').text

                if x.find('wiki/summary'):
                    self.wikiTextShort = x.find('wiki/summary').text

                if x.find('wiki/content'):
                    self.wikiTextFull = x.find('wiki/content').text

            url = urlopen( getTagTopTracksURL(quote(self.name), self.max_items) )
            tree = ET.parse(url)
            root = tree.getroot()

            for x in root.findall('tracks/track'):
                trackInfo = []

                artist = x.find('artist/name').text
                trackName = x.find('name').text
                trackImage = x.find('.//image[@size="extralarge"]').text

                trackInfo.append(artist)
                trackInfo.append(trackName)
                trackInfo.append(trackImage)
                self.topTracks.append(trackInfo)

            url = urlopen( getTagTopArtistsURL(quote(self.name), self.max_items) )
            tree = ET.parse(url)
            root = tree.getroot()

            for x in root.findall('topartists/artist'):
                artistInfo = []

                artist = x.find('name').text
                artistMBID = x.find('mbid').text
                artistImage = x.find('.//image[@size="mega"]').text

                artistInfo.append(artist)
                artistInfo.append(artistMBID)
                artistInfo.append(artistImage)
                self.topArtists.append(artistInfo)

            url = urlopen( getTagTopAlbumsURL(quote(self.name), self.max_items) )
            tree = ET.parse(url)
            root = tree.getroot()

            for x in root.findall('albums/album'):
                albumInfo = []

                album = x.find('name').text
                albumArtist = x.find('artist/name').text
                albumImage = x.find('.//image[@size="extralarge"]').text

                albumInfo.append(album)
                albumInfo.append(albumArtist)
                albumInfo.append(albumImage)
                self.topAlbums.append(albumInfo)

    def getName(self):
        return self.name

    def getTopAlbums(self):
        return self.topAlbums

    def getTopArtists(self):
        return self.topArtists

    def getTopTracks(self):
        return self.topTracks

    def getWikiShort(self):
        return self.wikiTextShort

    def getWikiFull(self):
        return self.wikiTextFull

    def __str__(self):
        string = 'Tag: ' + self.name

        if self.topAlbums:
            string += '\n\t' + 'Top Albums: '+ str(self.topAlbums)
        if self.topTracks:
            string += '\n\t' + 'Top Tracks: ' + str(self.topTracks)
        if self.topArtists:
            string += '\n\t' + 'Top Artists: '+ str(self.topArtists)
        if self.wikiTextShort:
            string += '\n\t' + 'Wiki (short): '+ self.wikiTextShort

        return string