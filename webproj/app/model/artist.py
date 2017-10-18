import html
import re
import xml.etree.ElementTree as ET
from urllib.parse import quote
from urllib.request import urlopen
from urllib.error import HTTPError
from ..api.urls import getArtistInfoURL, getArtistTopAlbumsIDURL, getArtistTopTracksIDURL, getArtistTopAlbumsURL, getArtistTopTracksURL
from ..db.BaseXClient import Session

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
            print('Fetching from database')
            self.fetchInfoDatabase()
        else:
            print('Fetching from API')
            self.fetchInfo()
            self.putInDatabase()

    def fetchInfoDatabase(self):
        result = False
        session = Session('localhost', 1984, 'admin', 'admin')

        try:
            query = "let $artists := collection('xpand-db')//artist " + \
                    "for $artist in $artists where $artist/name = '" + self.name + "' " + \
                    "return <result>{$artist}</result>"

            queryObj = session.query(query)

            # loop through all results
            for typecode, item in queryObj.iter():
                result = item

            queryObj.close()

        except Exception as e:
            print("fetchInfoDatabase")
            print("Something failed on XML Database!")

        finally:
            if session:
                session.close()

            if result:
                root = ET.fromstring(result)

                for tag in root.findall('./artist'):
                    self.name = html.unescape(tag.find('name').text)
                    self.mbid = tag.find('mbid').text
                    self.image = tag.find('image').text
                    self.biographyShort = html.unescape(tag.find('bioShort').text)
                    self.biographyFull = html.unescape(tag.find('bioFull').text)

                    for artist in tag.findall('similar/artist'):
                        similar = []
                        similar.append(html.unescape(artist.find('name').text))
                        similar.append(artist.find('image').text)
                        self.similarArtists.append(similar)

                    for topAlbum in tag.findall('topAlbums/topAlbum'):
                        albumInfo = []
                        albumInfo.append(html.unescape(topAlbum.find('name').text))
                        albumInfo.append(topAlbum.find('image').text)
                        self.topAlbums.append(albumInfo)

                    for topTrack in tag.findall('topTracks/topTrack'):
                        trackInfo = []
                        trackInfo.append(html.unescape(topTrack.find('name').text))
                        trackInfo.append(topTrack.find('image').text)
                        self.topTracks.append(trackInfo)

                    for tagInfo in tag.findall('tags/tag'):
                        self.tags.append(tagInfo.text)



    def checkDatabase(self):
        result = False
        session = Session('localhost', 1984, 'admin', 'admin')

        try:
            query = "let $artists := collection('xpand-db')/artists " + \
                    "return boolean($artists/artist/name/text() = '" + self.name + "')"

            queryObj = session.query(query)

            #loop through all results
            for typecode, item in queryObj.iter():
                result = item

            queryObj.close()

        except Exception as e:
            print("exception caught: checkDatabase")
            print(e)
            print("Something failed on XML Database!")

        finally:
            if session:
                session.close()

            if result == 'true':
                return True
            return False

    def putInDatabase(self):
        print("putInDatabase function")
        session = Session('localhost', 1984, 'admin', 'admin')

        try:
            query = "let $artists := collection('xpand-db')/artists " + \
                    "let $node := " + \
                    "<artist>" + \
                    "<name>" + html.escape(self.name) + "</name>" + \
                    "<mbid>" + self.mbid + "</mbid>" + \
                    "<image>" + self.image + "</image>" + \
                    "<bioShort>" + html.escape(self.biographyShort) + "</bioShort>" + \
                    "<bioFull>" + html.escape(self.biographyFull) + "</bioFull>" + \
                    "<similar>"

            for similarArtist in self.similarArtists:
                query += "<artist>" + \
                         "<name>" + html.escape(similarArtist[0]) + "</name>" + \
                         "<image>" + similarArtist[1] + "</image>" + \
                         "</artist>"

            query += "</similar>" + \
                     "<albums></albums>" + \
                     "<topAlbums>"

            for topAlbum in self.topAlbums:
                query += "<topAlbum>" + \
                         "<name>" + html.escape(topAlbum[0]) + "</name>" + \
                         "<image>" + topAlbum[1] + "</image>" + \
                         "</topAlbum>"

            query += "</topAlbums>" + \
                     "<topTracks>"

            for topTrack in self.topTracks:
                query += "<topTrack>" + \
                         "<name>" + html.escape(topTrack[0]) + "</name>" + \
                         "<image>" + topTrack[1] + "</image>" + \
                         "</topTrack>"

            query += "</topTracks>" + \
                     "<tags>"

            for tag in self.tags:
                query += "<tag>" + tag + "</tag>"

            query += "</tags>" + \
                     "</artist> " + \
                     "return insert node $node into $artists"

            queryObj = session.query(query)

            queryObj.execute()

            queryObj.close()

        except Exception as e:
            print("putInDatabase")
            print(e)
            print("Something failed on XML Database!")

        finally:
            if session:
                session.close()

    def fetchInfo(self):
        try:
            url = urlopen( getArtistInfoURL(quote(self.name)) )
            print(getArtistInfoURL(quote(self.name)))
        except HTTPError:
            print("fetchInfo")
            print('Artist doesn\'t exist!')
        else:
            tree = ET.parse(url)
            root = tree.getroot()

            for x in root.findall('artist'):
                if x.findall('bio/summary'):
                    txtShort = str(x.find('bio/summary').text)
                    self.biographyShort = txtShort.split('<a href=')[0]

                if x.findall('bio/content'):
                    txtFull = str(x.find('bio/content').text)
                    self.biographyFull = txtFull.split('<a href=')[0]

                if x.findall('.//image[@size="mega"]'):
                    self.image = x.find('.//image[@size="mega"]').text

                if x.findall('name'):
                    self.name = x.find('name').text

                if x.findall('mbid'):
                    self.mbid = x.find('mbid').text

                if x.findall('similar/artist'):
                    for y in x.findall('similar/artist'):
                        if y:
                            similar = []
                            similar.append(y.find('name').text)
                            similar.append(y.find('.//image[@size="mega"]').text)
                            self.similarArtists.append(similar)

                if x.findall('tags/tag'):
                    for tag in x.findall('tags/tag'):
                        if tag:
                            self.tags.append(tag.find('name').text)

            if self.mbid:
                url = urlopen(getArtistTopAlbumsIDURL(self.mbid, self.max_items))
            else:
                url = urlopen( getArtistTopAlbumsURL(self.name, self.max_items) )

            tree = ET.parse(url)
            root = tree.getroot()

            for album in root.findall('topalbums/album'):
                albumInfo = []

                albumName = album.find('name').text
                albumImage = album.find('.//image[@size="extralarge"]').text

                albumInfo.append(albumName)
                albumInfo.append(albumImage)
                self.topAlbums.append(albumInfo)

            if self.mbid:
                url = urlopen( getArtistTopTracksIDURL(self.mbid, self.max_items) )
            else:
                url = urlopen( getArtistTopTracksURL(self.name, self.max_items) )

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