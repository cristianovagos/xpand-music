import xml.etree.ElementTree as ET
from urllib.parse import quote
from urllib.request import urlopen
from urllib.error import HTTPError
from webproj.app.api.urls import getTrackInfoIDURL, getTrackInfoURL

class Track:

    def __init__(self, artist, name, mbid=None):
        self.name = name
        self.artist = artist
        self.mbid = mbid
        self.duration = None
        self.position = None
        self.topTags = []
        self.wikiTextShort = None
        self.wikiTextFull = None
        self.albumMBID = None

        self.fetchInfo()

    def fetchInfo(self):
        try:
            if self.mbid:
                url = urlopen(getTrackInfoIDURL(quote(self.mbid)))

                print( getTrackInfoIDURL(quote(self.mbid)) )
            else:
                url = urlopen(getTrackInfoURL(quote(self.name), quote(self.artist)))

                print( getTrackInfoURL(quote(self.name), quote(self.artist)) )
        except HTTPError:
            print('Track doesn\'t exist!')
        else:
            tree = ET.parse(url)
            root = tree.getroot()

            for x in root.findall('track'):
                self.name = x.find('name').text
                self.mbid = x.find('mbid').text
                self.artist = x.find('artist/name').text

                millis = int(x.find('duration').text)
                seconds = int((millis/1000)%60)
                minutes = int((millis/(1000*60))%60)
                self.duration = (str(minutes) + ":" + "%02d" % seconds)

                self.position = x.find('album').get('position')

                if x.find('wiki/summary'):
                    self.wikiTextShort = x.find('wiki/summary').text
                if x.find('wiki/content'):
                    self.wikiTextFull = x.find('wiki/content').text
                self.albumMBID = x.find('album/mbid').text

                for tag in x.findall('toptags/tag'):
                    self.topTags.append(tag.find('name').text)

    def getName(self):
        return self.name

    def getMBID(self):
        return self.mbid

    def getArtist(self):
        return self.artist

    def getDuration(self):
        return self.duration

    def getPosition(self):
        return self.position

    def getWikiShort(self):
        return self.wikiTextShort

    def getWikiFull(self):
        return self.wikiTextFull

    def getAlbumMBID(self):
        return self.albumMBID

    def getTopTags(self):
        return self.topTags

    def __str__(self):
        string = 'Track: ' + self.name

        if self.position:
            string += '\n\t' + 'Position: ' + self.position
        if self.artist:
            string += '\n\t' + 'Artist: ' + self.artist
        if self.mbid:
            string += '\n\t' + 'MBID: ' + self.mbid
        if self.duration:
            string += '\n\t' + 'Duration: ' + self.duration
        if self.albumMBID:
            string += '\n\t' + 'Album MBID: ' + self.albumMBID
        if self.wikiTextShort:
            string += '\n\t' + 'Wiki (short): ' + self.wikiTextShort
        if self.topTags:
            string += '\n\t' + 'Top Tags: ' + str(self.topTags)

        return string


