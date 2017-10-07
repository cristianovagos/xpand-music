import xml.etree.ElementTree as ET
from urllib.parse import quote
from urllib.request import urlopen
from urllib.error import HTTPError
from webproj.app.api.urls import getArtistInfoURL, getArtistTopAlbumsIDURL, getArtistTopTracksIDURL

class Artist:

    def __init__(self, name, max_items=5):
        self.name = name
        self.mbid = None
        self.image = None
        self.biographyShort = None
        self.biographyFull = None
        self.similarArtists = []
        self.albums = []
        self.topTracks = []
        self.topAlbums = []
        self.tags = []

        self.max_items = max_items

        self.fetchInfo()

    def fetchInfo(self):
        try:
            url = urlopen( getArtistInfoURL(quote(self.name)) )
        except HTTPError:
            print('Artist doesn\'t exist!')
        else:
            tree = ET.parse(url)
            root = tree.getroot()

            for x in root.findall('artist'):
                self.biographyShort = x.find('bio/summary').text
                self.biographyFull = x.find('bio/content').text
                self.image = x.find('.//image[@size="mega"]').text
                self.name = x.find('name').text
                self.mbid = x.find('mbid').text

                for y in x.findall('similar/artist'):
                    similar = []
                    similar.append(y.find('name').text)
                    similar.append(y.find('.//image[@size="mega"]').text)
                    self.similarArtists.append(similar)

                for tag in x.findall('tags/tag'):
                    self.tags.append(tag.find('name').text)

            url = urlopen( getArtistTopAlbumsIDURL(self.mbid, self.max_items) )
            tree = ET.parse(url)
            root = tree.getroot()

            for album in root.findall('topalbums/album'):
                albumInfo = []

                albumName = album.find('name').text
                albumImage = album.find('.//image[@size="extralarge"]').text

                albumInfo.append(albumName)
                albumInfo.append(albumImage)
                self.topAlbums.append(albumInfo)

            url = urlopen( getArtistTopTracksIDURL(self.mbid, self.max_items) )
            tree = ET.parse(url)
            root = tree.getroot()

            for track in root.findall('toptracks/track'):
                trackInfo = []

                trackName = track.find('name').text
                trackImage = track.find('.//image[@size="extralarge"]').text

                trackInfo.append(trackName)
                trackInfo.append(trackImage)
                self.topTracks.append(trackInfo)


    def getName(self):
        return self.name

    def getMBID(self):
        return self.mbid

    def getImage(self):
        return self.image

    def getBiography(self, short=False):
        if short:
            return self.biographyShort
        return self.biographyFull

    def getSimilarArtists(self):
        return self.similarArtists

    def getAlbums(self):
        return self.albums

    def getTopAlbums(self):
        return self.topAlbums

    def getTopTracks(self):
        return self.topTracks

    def __str__(self):
        string = 'Artist: ' + self.name

        if self.mbid:
            string += '\n\t' + 'MBID: ' + self.mbid
        if self.biographyShort:
            string += '\n\t' + 'Biography: ' + self.biographyShort
        if self.similarArtists:
            string += '\n\t' + 'Similar Artists: ' + str(self.similarArtists)
        if self.albums:
            string += '\n\t' + 'Albums: ' + str(self.albums)
        if self.topAlbums:
            string += '\n\t' + 'Top Albums: '+ str(self.topAlbums)
        if self.topTracks:
            string += '\n\t' + 'Top Tracks: ' + str(self.topTracks)

        return string