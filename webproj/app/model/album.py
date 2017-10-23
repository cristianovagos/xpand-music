import html
import xml.etree.ElementTree as ET
from urllib.parse import quote
from urllib.request import urlopen
from urllib.error import HTTPError
#from webproj.app.model.track import Track
from ..model.artist import Artist
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
        self.comments = []
        self.wikiTextShort = None
        self.wikiTextFull = None

        self.noAlbumImage = self.noTrackImage = "https://www.shareicon.net/data/2015/07/09/66681_music_512x512.png"
        self.noWikiText = "Sorry, no wiki available for this album."

        self.albumExists = True

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
                    if tag.findall('name'):
                        self.name = html.unescape(tag.find('name').text)

                    if tag.findall('mbid'):
                        self.mbid = tag.find('mbid').text

                    if tag.findall('image'):
                        self.image = tag.find('image').text

                    self.wikiTextShort = html.unescape(tag.find('wikiShort').text)
                    self.wikiTextFull = html.unescape(tag.find('wikiFull').text)

                    if tag.findall('tracks/track'):
                        for track in tag.findall('tracks/track'):
                            self.tracks.append(html.unescape(track.find('name').text))

                    if tag.findall('tags/tag'):
                        for tagInfo in tag.findall('tags/tag'):
                            self.tags.append(tagInfo.text)

                    if tag.findall('comments/comment'):
                        for comment in tag.findall('comments/comment'):
                            if comment:
                                commentInfo = []

                                if comment.findall('user'):
                                    commentInfo.append(comment.find('user').text)
                                else:
                                    continue

                                if comment.findall('text'):
                                    commentInfo.append(html.unescape(comment.find('text').text))

                                if comment.findall('id'):
                                    commentInfo.append(comment.find('id').text)

                                self.comments.append(commentInfo)

    def putInDatabase(self):
        session = Session('localhost', 1984, 'admin', 'admin')

        try:
            result = None
            query = "let $artists := collection('xpand-db')/artists " + \
                    "return boolean($artists/artist/name/text() = '" + self.name + "')"

            queryObj = session.query(query)

            # loop through all results
            for typecode, item in queryObj.iter():
                result = item

            queryObj.close()

            if result == 'false':
                Artist(self.artist)

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
                     "<comments></comments> " + \
                     "</album> " + \
                     "return insert node $node into $insertpath"

            queryObj = session.query(query)

            queryObj.execute()

            queryObj.close()

        except Exception as e:
            print("Something failed on XML Database!")
            print(e)

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
            print(e)

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
            self.albumExists = False
        else:
            tree = ET.parse(url)
            root = tree.getroot()

            for x in root.findall('album'):
                if x:
                    if x.findall('name'):
                        self.name = x.find('name').text

                    if x.findall('mbid'):
                        self.mbid = x.find('mbid').text

                    if x.findall('.//image[@size="mega"]'):
                        self.image = x.find('.//image[@size="mega"]').text
                    else:
                        self.image = self.noAlbumImage

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

                    if x.findall('tracks/track'):
                        for track in x.findall('tracks/track'):
                            if track:
                                if track.find('name').text:
                                    trackName = track.find('name').text
                                    self.tracks.append(trackName)
                                    #self.tracks.append(Track(self.artist, trackName))

                    if x.findall('tags/tag'):
                        for tag in x.findall('tags/tag'):
                            if tag:
                                if tag.find('name').text:
                                    tagText = tag.find('name').text
                                    self.tags.append(tagText)


    def changeComment(self, numComment, newText):
        session = Session('localhost', 1984, 'admin', 'admin')

        try:
            query = "let $artists := collection('xpand-db')//artist " + \
                    "for $artist in $artists where $artist/name = '" + self.artist + "' " + \
                    "let $comment := $artist//album[name='" + self.name + "']/comments/comment[id='" + numComment + "'] " + \
                    "return replace value of node $comment/text with '" + html.escape(newText) + "' "

            queryObj = session.query(query)
            queryObj.execute()
            queryObj.close()

        except Exception as e:
            print("changeComment")
            print("Something failed on XML Database!")

        finally:
            if session:
                session.close()


    def deleteComment(self, numComment):
        session = Session('localhost', 1984, 'admin', 'admin')

        try:
            query = "let $artists := collection('xpand-db')//artist " + \
                    "for $artist in $artists where $artist/name = '" + self.artist + "' " + \
                    "let $comment := $artist//album[name='" + self.name + "']/comments/comment[id='" + numComment + "'] " + \
                    "return delete node $comment "

            queryObj = session.query(query)
            queryObj.execute()
            queryObj.close()

        except Exception as e:
            print("deleteComment")
            print("Something failed on XML Database!")

        finally:
            if session:
                session.close()


    def storeComment(self, user, text):
        session = Session('localhost', 1984, 'admin', 'admin')

        try:
            numComments = 0
            query = "let $artists := collection('xpand-db')//artist " + \
                    "for $artist in $artists where $artist/name = '" + self.artist + "' " + \
                    "return count($artist//album[name='" + self.name + "']/comments/comment) "

            queryObj = session.query(query)

            # loop through all results
            for typecode, item in queryObj.iter():
                numComments = int(item)

            queryObj.close()

            query = "let $artists := collection('xpand-db')//artist " + \
                    "for $artist in $artists where $artist/name = '" + self.artist + "' " + \
                    "let $insertpath := $artist//album[name='" + self.name + "']/comments " + \
                    "let $node := <comment>" + \
                    "<id>" + str((numComments+1)) + "</id>" + \
                    "<user>" + user + "</user>" + \
                    "<text>" + html.escape(text) + "</text>" + \
                    "</comment> " + \
                    "return insert node $node into $insertpath"

            queryObj = session.query(query)
            queryObj.execute()
            queryObj.close()

        except Exception as e:
            print("comment")
            print("Something failed on XML Database!")

        finally:
            if session:
                session.close()

    def exists(self):
        return self.albumExists

    def getComments(self):
        return self.comments

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