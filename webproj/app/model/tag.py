import xml.etree.ElementTree as ET
from urllib.parse import quote
from urllib.request import urlopen
from urllib.error import HTTPError
from ..api.urls import getTagInfoURL, getTagTopAlbumsURL, \
    getTagTopArtistsURL, getTagTopTracksURL

class Tag:

    def __init__(self, name, max_items=5):
        self.name = name
        self.topAlbums = []
        self.topArtists = []
        self.topTracks = []
        self.wikiTextShort = None
        self.wikiTextFull = None

        self.max_items = max_items
        self.noWikiText = "Sorry, there's no wiki available for this tag."
        self.noAlbumImage = self.noTrackImage = "https://www.shareicon.net/data/2015/07/09/66681_music_512x512.png"
        self.noArtistImage = "http://paradeal.pp.ua/img/no-user.jpg"

        self.fetchInfo()

    def fetchInfo(self):
        try:
            print(getTagInfoURL(quote(self.name)))
            url = urlopen( getTagInfoURL(quote(self.name)) )
        except HTTPError:
            print('Tag doesn\'t exist!')
        else:
            tree = ET.parse(url)
            root = tree.getroot()

            for x in root.findall('tag'):
                self.name = x.find('name').text

                if x.findall('wiki/summary'):
                    if x.find('wiki/summary').text != None:
                        txtShort = str(x.find('wiki/summary').text)
                        txtShort = txtShort.split('<a href=')[0]

                        if len(txtShort) < 5:
                            self.wikiTextShort = self.noWikiText
                        else:
                            self.wikiTextShort = txtShort
                    else:
                        self.wikiTextShort = self.noWikiText
                else:
                    self.wikiTextShort = self.noWikiText

                if x.findall('wiki/content'):
                    if x.find('wiki/content').text != None:
                        txtFull = str(x.find('wiki/content').text)
                        txtFull = txtFull.split('<a href=')[0]

                        if len(txtFull) < 5:
                            self.wikiTextFull = self.noWikiText
                        else:
                            self.wikiTextFull = txtFull
                    else:
                        self.wikiTextFull = self.noWikiText
                else:
                    self.wikiTextFull = self.noWikiText

            url = urlopen( getTagTopTracksURL(quote(self.name), self.max_items) )
            tree = ET.parse(url)
            root = tree.getroot()

            for x in root.findall('tracks/track'):
                trackInfo = []

                artist = x.find('artist/name').text
                trackName = x.find('name').text

                if x.findall('.//image[@size="extralarge"]'):
                    trackImage = x.find('.//image[@size="extralarge"]').text
                else:
                    trackImage = self.noTrackImage

                trackInfo.append(artist)
                trackInfo.append(trackName)
                trackInfo.append(trackImage)
                self.topTracks.append(trackInfo)

            url = urlopen( getTagTopArtistsURL(quote(self.name), self.max_items) )
            tree = ET.parse(url)
            root = tree.getroot()

            for x in root.findall('topartists/artist'):
                artistMBID = None
                artistInfo = []

                artist = x.find('name').text

                if x.findall('mbid'):
                    artistMBID = x.find('mbid').text

                if x.findall('.//image[@size="mega"]'):
                    artistImage = x.find('.//image[@size="mega"]').text
                else:
                    artistImage = self.noArtistImage

                artistInfo.append(artist)

                if artistMBID:
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

                if x.findall('.//image[@size="extralarge"]'):
                    albumImage = x.find('.//image[@size="extralarge"]').text
                else:
                    albumImage = self.noAlbumImage

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