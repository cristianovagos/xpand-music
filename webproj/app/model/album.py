import html
import xml.etree.ElementTree as ET
from urllib.parse import quote
from urllib.request import urlopen
from urllib.error import HTTPError
#from webproj.app.model.track import Track
from ..api.urls import getAlbumInfoURL, getAlbumInfoIDURL
from ..db.BaseXClient import Session

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

        if (self.checkDatabase()):
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
                    "for $artist in $artists where $artist/name = '" + self.artist + "' " + \
                    "return <result>{$artist//album[name='" + self.name + "']}</result>"

            queryObj = session.query(query)

            # loop through all results
            for typecode, item in queryObj.iter():
                result = item

            queryObj.close()

        except Exception as e:
            print("Something failed on XML Database!")

        finally:
            if session:
                session.close()

            if result:
                root = ET.fromstring(result)

                for tag in root.findall('./album'):
                    self.name = html.unescape(tag.find('name').text)
                    self.mbid = tag.find('mbid').text
                    self.image = tag.find('image').text
                    self.wikiTextShort = html.unescape(tag.find('wikiShort').text)
                    self.wikiTextFull = html.unescape(tag.find('wikiFull').text)

                    for track in tag.findall('tracks/track'):
                        trackInfo = []
                        trackInfo.append(html.unescape(track.find('name').text))
                        self.tracks.append(trackInfo)

                    for tagInfo in tag.findall('tags/tag'):
                        self.tags.append(tagInfo.text)

    def putInDatabase(self):
        session = Session('localhost', 1984, 'admin', 'admin')

        try:
            query = "let $artists := collection('xpand-db')//artist " + \
                    "let $insertpath := $artists[name='" + self.artist + "']/albums " + \
                    "let $node := " + \
                    "<album>" + \
                    "<name>" + html.escape(self.name) + "</name>" + \
                    "<mbid>" + self.mbid + "</mbid>" + \
                    "<image>" + self.image + "</image>" + \
                    "<wikiShort>" + html.escape(self.wikiTextShort) + "</wikiShort>" + \
                    "<wikiFull>" + html.escape(self.wikiTextFull) + "</wikiFull>" + \
                    "<tracks>"

            for track in self.tracks:
                query += "<track>" + \
                         "<name>" + html.escape(track) + "</name>" + \
                         "</track> "

            query += "</tracks> " + \
                     "<tags>"

            for tag in self.tags:
                query += "<tag>" + tag + "</tag>"

            query += "</tags> " + \
                     "</album> " + \
                     "return insert node $node into $insertpath"

            queryObj = session.query(query)

            queryObj.execute()

            queryObj.close()

        except Exception as e:
            print("Something failed on XML Database!")

        finally:
            if session:
                session.close()


    def checkDatabase(self):
        result = False
        session = Session('localhost', 1984, 'admin', 'admin')

        try:
            query = "let $artists := collection('xpand-db')/artists " + \
                    "let $albums := $artists/artist/albums " + \
                    "return boolean($artists/artist/name/text() = '" + self.artist + \
                    "' and $albums/album/name/text() = '" + self.name + "')"

            queryObj = session.query(query)

            # loop through all results
            for typecode, item in queryObj.iter():
                result = item

            queryObj.close()

        except Exception as e:
            print("Something failed on XML Database!")

        finally:
            if session:
                session.close()

            if result == 'true':
                return True
            return False

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