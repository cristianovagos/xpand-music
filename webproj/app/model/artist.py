import html
import xml.etree.ElementTree as ET
from urllib.parse import quote
from urllib.request import urlopen
from urllib.error import HTTPError
from ..api.urls import getArtistInfoURL, getArtistTopAlbumsIDURL, \
    getArtistTopTracksIDURL, getArtistTopAlbumsURL, getArtistTopTracksURL
from ..db.BaseXClient import Session

class Artist:

    def __init__(self, name, max_items=5):
        self.name = name
        self.mbid = None
        self.image = "http://paradeal.pp.ua/img/no-user.jpg"
        self.biographyShort = None
        self.biographyFull = None
        self.similarArtists = []
        self.albums = []
        self.topTracks = []
        self.topAlbums = []
        self.tags = []
        self.comments = []

        self.max_items = max_items

        self.noArtistImage = "http://paradeal.pp.ua/img/no-user.jpg"
        self.noAlbumImage = self.noTrackImage = "https://www.shareicon.net/data/2015/07/09/66681_music_512x512.png"
        self.noBioText = "Artist Biography not available, sorry."

        self.artistExists = True

        if self.checkDatabase():
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
                    if tag.findall('name'):
                        self.name = html.unescape(tag.find('name').text)

                    if tag.findall('mbid'):
                        self.mbid = tag.find('mbid').text

                    if tag.findall('image'):
                        self.image = tag.find('image').text

                    if tag.findall('bioShort'):
                        self.biographyShort = html.unescape(tag.find('bioShort').text)
                    else:
                        self.biographyShort = self.noBioText

                    if tag.findall('bioFull'):
                        self.biographyFull = html.unescape(tag.find('bioFull').text)
                    else:
                        self.biographyFull = self.noBioText

                    if tag.findall('similar/artist'):
                        for artist in tag.findall('similar/artist'):
                            if artist:
                                similar = []

                                if artist.findall('name'):
                                    similar.append(html.unescape(artist.find('name').text))
                                else:
                                    continue

                                if artist.findall('image'):
                                    if artist.find('image').text != None:
                                        similar.append(artist.find('image').text)
                                    else:
                                        similar.append(self.noArtistImage)

                                self.similarArtists.append(similar)

                    if tag.findall('topAlbums/topAlbum'):
                        for topAlbum in tag.findall('topAlbums/topAlbum'):
                            if topAlbum:
                                albumInfo = []

                                if topAlbum.findall('name'):
                                    albumInfo.append(html.unescape(topAlbum.find('name').text))
                                else:
                                    continue

                                if topAlbum.findall('image'):
                                    if topAlbum.find('image').text != None:
                                        albumInfo.append(topAlbum.find('image').text)
                                    else:
                                        albumInfo.append(self.noAlbumImage)

                                self.topAlbums.append(albumInfo)

                    if tag.findall('topTracks/topTrack'):
                        for topTrack in tag.findall('topTracks/topTrack'):
                            if topTrack:
                                trackInfo = []

                                if topTrack.findall('name'):
                                    trackInfo.append(html.unescape(topTrack.find('name').text))
                                else:
                                    continue

                                if topTrack.findall('image'):
                                    trackInfo.append(topTrack.find('image').text)
                                else:
                                    trackInfo.append(self.noTrackImage)

                                self.topTracks.append(trackInfo)

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

                                self.comments.append(commentInfo)


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
                     "<comments></comments> " + \
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
        except HTTPError:
            print('Artist doesn\'t exist!')
            self.artistExists = False
        else:
            tree = ET.parse(url)
            root = tree.getroot()

            for x in root.findall('artist'):
                if x.findall('bio/summary'):
                    if x.find('bio/summary').text != None:
                        txtShort = str(x.find('bio/summary').text)
                        txtShort = txtShort.split('<a href=')[0]

                        if len(txtShort) < 5:
                            self.biographyShort = self.noBioText
                        else:
                            self.biographyShort = txtShort
                    else:
                        self.biographyShort = self.noBioText
                else:
                    self.biographyShort = self.noBioText

                if x.findall('bio/content'):
                    if x.find('bio/content').text != None:
                        txtFull = str(x.find('bio/content').text)
                        txtFull = txtFull.split('<a href=')[0]

                        if len(txtFull) < 5:
                            self.biographyFull = self.noBioText
                        else:
                            self.biographyFull = txtFull
                    else:
                        self.biographyFull = self.noBioText
                else:
                    self.biographyFull = self.noBioText

                if x.findall('.//image[@size="mega"]'):
                    if x.find('.//image[@size="mega"]').text != None:
                        self.image = x.find('.//image[@size="mega"]').text
                    else:
                        self.image = self.noArtistImage

                if x.findall('name'):
                    self.name = x.find('name').text

                if x.findall('mbid'):
                    self.mbid = x.find('mbid').text

                if x.findall('similar/artist'):
                    for y in x.findall('similar/artist'):
                        if y:
                            similar = []

                            if y.findall('name'):
                                similar.append(y.find('name').text)
                            else:
                                continue

                            if y.findall('.//image[@size="mega"]'):
                                if y.find('.//image[@size="mega"]').text != None:
                                    similar.append(y.find('.//image[@size="mega"]').text)
                                else:
                                    similar.append(self.noArtistImage)

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

            if root.findall('topalbums/album'):
                for album in root.findall('topalbums/album'):
                    if album:
                        albumInfo = []

                        if album.findall('name'):
                            albumInfo.append(album.find('name').text)
                        else:
                            continue

                        if album.findall('.//image[@size="extralarge"]'):
                            if album.find('.//image[@size="extralarge"]').text != None:
                                albumInfo.append(album.find('.//image[@size="extralarge"]').text)
                            else:
                                albumInfo.append(self.noAlbumImage)

                        self.topAlbums.append(albumInfo)

            if self.mbid:
                url = urlopen( getArtistTopTracksIDURL(self.mbid, self.max_items) )
            else:
                url = urlopen( getArtistTopTracksURL(self.name, self.max_items) )

            tree = ET.parse(url)
            root = tree.getroot()

            if root.findall('toptracks/track'):
                for track in root.findall('toptracks/track'):
                    if track:
                        trackInfo = []

                        if track.findall('name'):
                            trackName = track.find('name').text
                        else:
                            continue

                        if track.findall('.//image[@size="extralarge"]'):
                            trackImage = track.find('.//image[@size="extralarge"]').text
                        else:
                            trackImage = self.noTrackImage

                        trackInfo.append(trackName)
                        trackInfo.append(trackImage)
                        self.topTracks.append(trackInfo)


    def storeComment(self, user, text):
        session = Session('localhost', 1984, 'admin', 'admin')

        try:
            numComments = 0
            query = "let $artists := collection('xpand-db')//artist " + \
                    "for $artist in $artists where $artist/name = '" + self.name + "' " + \
                    "return count($artist/comments/comment) "

            queryObj = session.query(query)

            # loop through all results
            for typecode, item in queryObj.iter():
                numComments = int(item)

            queryObj.close()

            query = "let $artists := collection('xpand-db')//artist " + \
                    "for $artist in $artists where $artist/name = '" + self.name + "' " + \
                    "let $insertpath := $artist/comments " + \
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
            print(e)
            print("Something failed on XML Database!")

        finally:
            if session:
                session.close()

    def changeComment(self, numComment, newText):
        session = Session('localhost', 1984, 'admin', 'admin')

        try:
            query = "let $artists := collection('xpand-db')//artist " + \
                    "for $artist in $artists where $artist/name = '" + self.name + "' " + \
                    "let $comment := $artist/comments/comment[id='" + numComment + "'] " + \
                    "return replace value of node $comment/text with '" + html.escape(newText) + "' "

            queryObj = session.query(query)
            queryObj.execute()
            queryObj.close()

        except Exception as e:
            print("changeComment")
            print(e)
            print("Something failed on XML Database!")

        finally:
            if session:
                session.close()


    def deleteComment(self, numComment):
        session = Session('localhost', 1984, 'admin', 'admin')

        try:
            query = "let $artists := collection('xpand-db')//artist " + \
                    "for $artist in $artists where $artist/name = '" + self.name + "' " + \
                    "let $comment := $artist/comments/comment[id='" + numComment + "'] " + \
                    "return delete node $comment "

            queryObj = session.query(query)
            queryObj.execute()
            queryObj.close()

        except Exception as e:
            print("deleteComment")
            print(e)
            print("Something failed on XML Database!")

        finally:
            if session:
                session.close()


    def exists(self):
        return self.artistExists

    def getComments(self):
        return self.comments

    def getTags(self):
        return self.tags

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
        if self.tags:
            string += '\n\t' + 'Tags: ' + str(self.tags)

        return string