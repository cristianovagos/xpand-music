import xml.etree.ElementTree as ET
from urllib.parse import quote
from urllib.request import urlopen
from urllib.error import HTTPError
from webproj.app.model.track import Track
from webproj.app.api.urls import getAlbumInfoURL, getAlbumInfoIDURL

class Album:

    def __init__(self, name, artist, mbid=None):
        self.name = name
        self.artist = artist
        self.mbid = mbid
        self.image = None
        self.tracks = []
        self.tags = []
        self.wikiTextShort = None
        self.wikiTextFull = None

        self.fetchInfo()

    def fetchInfo(self):
        try:
            if self.mbid:
                url = urlopen( getAlbumInfoIDURL(quote(self.mbid)) )
            else:
                url = urlopen( getAlbumInfoURL(quote(self.artist), quote(self.name)) )
        except HTTPError:
            print('Album doesn\'t exist!')
        else:
            tree = ET.parse(url)
            root = tree.getroot()

            for x in root.findall('album'):
                self.name = x.find('name').text
                self.mbid = x.find('mbid').text
                self.image = x.find('.//image[@size="mega"]').text
                self.wikiTextShort = x.find('wiki/summary').text
                self.wikiTextFull = x.find('wiki/content').text

                for track in x.findall('tracks/track'):
                    trackName = track.find('name').text
                    self.tracks.append(trackName)
                    #self.tracks.append(Track(self.artist, trackName))

                for tag in x.findall('tags/tag'):
                    tagText = tag.find('name').text
                    self.tags.append(tagText)

    def getName(self):
        return self.name

    def getArtist(self):
        return self.artist

    def getMBID(self):
        return self.mbid

    def getImage(self):
        return self.image

    def getTracks(self):
        return self.tracks

    def getTags(self):
        return self.tags

    def getWikiShort(self):
        return self.wikiTextShort

    def getWikiFull(self):
        return self.wikiTextFull

    def __str__(self):
        string = 'Album: ' + self.name

        if self.artist:
            string += '\n\t' + 'Artist: ' + self.artist
        if self.mbid:
            string += '\n\t' + 'MBID: ' + self.mbid
        if self.wikiTextShort:
            string += '\n\t' + 'Wiki (short): ' + self.wikiTextShort
        if self.tracks:
            string += '\n\t' + 'Tracks: ' + str(self.tracks)
        if self.tags:
            string += '\n\t' + 'Tags: ' + str(self.tags)

        return string