import xml.etree.ElementTree as ET
from urllib.parse import quote
from urllib.request import urlopen
from urllib.error import HTTPError
from webproj.app.api.urls import getArtistInfoURL, getArtistTopAlbumsIDURL, getArtistTopTracksIDURL
from webproj.app.db.BaseXClient import Session

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

        if(self.checkDatabase()):
            self.fetchInfoDatabase()
        else:
            self.fetchInfo()
            self.putInDatabase()

    def checkDatabase(self):
        session = Session('localhost', 1984, 'admin', 'admin')

        try:
            query = "let $artists := collection('xpand-db')/artists " + \
                    "return boolean($artists/artist/name/text() = '" + self.name + "')"

            queryObj = session.query(query)

            # loop through all results
            for typecode, item in queryObj.iter():
                result = item

            queryObj.close()

        finally:
            if session:
                session.close()

            if result:
                return True
            return False

    def putInDatabase(self):
        session = Session('localhost', 1984, 'admin', 'admin')

        try:
            query = "let $artists := collection('xpand-db')/artists " + \
                    "let $node := " + \
                    "<artist> " + \
                    "   <name>" + self.name + "</name> " + \
                    "   <mbid>" + self.mbid + "</mbid> " + \
                    "   <image>" + self.image + "</image> " + \
                    "   <bioShort>" + self.biographyShort + "</bioShort> " + \
                    "   <bioFull>" + self.biographyFull + "</bioFull> " + \
                    "   <similar>"

            for similarArtist in self.similarArtists:
                query += "  <artist> " + \
                         "      <name>" + similarArtist[0] + "</name> " + \
                         "      <image>" + similarArtist[1] + "</image> " + \
                         "  </artist> "

            query += "  </similar> " + \
                     "  <albums></albums> " + \
                     "  <topAlbums> "

            for topAlbum in self.topAlbums:
                query += "  <topAlbum> " + \
                         "      <name>" + topAlbum[0] + "</name> " + \
                         "      <image>" + topAlbum[1] + "</image> " + \
                         "  </topAlbum> "

            query += "  </topAlbums> " + \
                     "  <topTracks> "

            for topTrack in self.topTracks:
                query += "  <topTrack> " + \
                         "      <name>" + topTrack[0] + "</name> " + \
                         "      <image>" + topTrack[1] + "</image> " + \
                         "  </topTrack> "

            query += "  </topTracks> " + \
                     "  <tags> "

            for tag in self.tags:
                query += "<tag>" + tag + "</tag> "

            query += "  </tags> " + \
                     "</artist> " + \
                     "return insert node $node into $artists"

            queryObj = session.query(query)
            print(session.info())

            queryObj.close()

        finally:
            if session:
                session.close()

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