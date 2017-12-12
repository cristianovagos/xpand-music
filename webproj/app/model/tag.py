import os, json, rdflib, lxml.etree as ETree
import xml.etree.ElementTree as ET
from urllib.parse import quote, unquote, urlparse
from urllib.request import urlopen
from urllib.error import HTTPError
from ..api.urls import getTagInfoURL, getTagTopAlbumsURL, \
    getTagTopArtistsURL, getTagTopTracksURL
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient

class Tag:

    def __init__(self, name, max_items=5, displayTop=True):
        self.name = name
        self.topAlbums = []
        self.topArtists = []
        self.topTracks = []
        self.wikiTextShort = None
        self.wikiTextFull = None

        self.displayTop = displayTop
        self.max_items = max_items
        self.noWikiText = "Sorry, there's no wiki available for this tag."
        self.noAlbumImage = self.noTrackImage = "https://www.shareicon.net/data/2015/07/09/66681_music_512x512.png"
        self.noArtistImage = "http://paradeal.pp.ua/img/no-user.jpg"

        # self.fetchInfo()

        if self.checkGraphDB():
            print("Fetching tag " + self.name + " from GraphDB")
            self.fetchInfoGraphDB()
        else:
            print("Fetching tag " + self.name + " from API")
            self.transformTagRDF()


    def checkGraphDB(self):
        endpoint = "http://localhost:7200"
        repo_name = "xpand-music"

        client = ApiClient(endpoint=endpoint)
        accessor = GraphDBApi(client)

        query = """
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                    PREFIX cs: <http://www.xpand.com/rdf/>
                    SELECT *
                    WHERE{
                        ?tag rdf:type cs:Tag .
                        ?tag foaf:name "%s" .
                        ?tag cs:playCount ?tagPlayCount
                    }
                """ % (quote(self.name))

        payload_query = {"query": query}
        res = accessor.sparql_select(body=payload_query,
                                     repo_name=repo_name)
        res = json.loads(res)

        for e in res['results']['bindings']:
            if (e['tag']['value']):
                return True
            return False


    def transformTagRDF(self):
        print("Transforming Tag (RDF)...")

        try:
            url = urlopen(getTagInfoURL(quote(self.name)))
        except HTTPError:
            print('Tag doesn\'t exist!')
        else:
            # Obter Current Working Directory
            currentPath = os.getcwd()

            # Transformacao da Tag para RDF
            xmlParsed = ETree.parse(url)

            tagXSLT = ETree.parse(open(currentPath + '/app/xml/transformTagRDF.xsl', 'r'))
            transform = ETree.XSLT(tagXSLT)
            finalTag = transform(xmlParsed)

            finalTag = str.replace(str(finalTag), '<?xml version="1.0"?>', '')

            # Criar grafo RDFLib, inserir o RDF/XML decorrente da transformação
            g = rdflib.Graph()
            g.parse(data=finalTag, format="application/rdf+xml")

            # dados para ligação ao GraphDB
            endpoint = "http://localhost:7200"
            repo_name = "xpand-music"

            # ligar ao GraphDB
            client = ApiClient(endpoint=endpoint)
            accessor = GraphDBApi(client)

            print("Inserting tag into GraphDB...")

            # Percorrer o grafo e inserir cada triplo (sujeito, predicado, objeto) no GraphDB
            for s, p, o in g:
                # verificar se o objeto é um URI
                if (urlparse(o).scheme and urlparse(o).netloc):
                    # URI
                    query = """
                                insert data {<%s> <%s> <%s>}
                            """ % (s, p, o)
                else:
                    # String
                    query = """
                                insert data {<%s> <%s> '%s'}
                            """ % (s, p, quote(o))

                # Enviar a query via API do GraphDB
                payload_query = {"update": query}
                res = accessor.sparql_update(body=payload_query,
                                             repo_name=repo_name)

            # Retirar dados do GraphDB e preencher atributos da classe
            self.fetchInfoGraphDB()


    def fetchInfoGraphDB(self):
        endpoint = "http://localhost:7200"
        repo_name = "xpand-music"

        client = ApiClient(endpoint=endpoint)
        accessor = GraphDBApi(client)

        query = """
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX cs: <http://www.xpand.com/rdf/>
                    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                    SELECT ?tag ?tagBiografia
                    WHERE{
                        ?tag rdf:type cs:Tag .
                        ?tag foaf:name "%s" .
                        ?tag cs:biography ?tagBiografia .
                    }
                """ % (quote(self.name))

        payload_query = {"query": query}
        res = accessor.sparql_select(body=payload_query,
                                     repo_name=repo_name)
        res = json.loads(res)

        tagURI = None
        for e in res['results']['bindings']:
            tagURI = e['tag']['value']
            self.wikiTextShort = unquote(e['tagBiografia']['value'])

        if not self.displayTop:
            return

        if not tagURI:
            print("Error fetching Tag URI. Fetching all data from API...")
            self.fetchInfo()
        else:
            # Obter top artists
            query = """
                        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                        PREFIX cs: <http://www.xpand.com/rdf/>
                        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                        SELECT ?artistName ?artistImage ?artistPlayCount
                        WHERE{
                            ?artist rdf:type cs:MusicArtist .
                            ?artist cs:Tag <%s> .
                            ?artist foaf:name ?artistName .
                            ?artist foaf:Image ?artistImage .
                            ?artist cs:playCount ?artistPlayCount .
                        }
                        ORDER BY DESC(xsd:integer(?artistPlayCount))
                    """ % (tagURI)

            payload_query = {"query": query}
            res = accessor.sparql_select(body=payload_query,
                                         repo_name=repo_name)
            res = json.loads(res)

            if len(res['results']['bindings']) > 0:
                for e in res['results']['bindings']:
                    topArtist = []

                    topArtist.append(unquote(e['artistName']['value']))
                    topArtist.append(e['artistImage']['value'])
                    topArtist.append(e['artistPlayCount']['value'])
                    self.topArtists.append(topArtist)

                self.topArtists = self.topArtists[:self.max_items]
            # else:
            #     print("Not enough artists to display. Fetching from API...")
            #     self.fetchTopArtists()

            # Obter top albums
            query = """
                        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                        PREFIX cs: <http://www.xpand.com/rdf/>
                        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                        SELECT ?albumName ?albumImage ?albumPlayCount ?artistName
                        WHERE{
                            ?album rdf:type cs:Album .
                            ?album cs:Tag <%s> .
                            ?album foaf:name ?albumName .
                            ?album foaf:Image ?albumImage .
                            ?album cs:playCount ?albumPlayCount .
                            ?album cs:MusicArtist ?artist .
                            ?artist foaf:name ?artistName .
                        }
                        ORDER BY DESC(xsd:integer(?albumPlayCount))
                    """ % (tagURI)

            payload_query = {"query": query}
            res = accessor.sparql_select(body=payload_query,
                                         repo_name=repo_name)
            res = json.loads(res)

            if len(res['results']['bindings']) > 0:
                for e in res['results']['bindings']:
                    topAlbum = []

                    topAlbum.append(unquote(e['albumName']['value']))
                    topAlbum.append(unquote(e['artistName']['value']))
                    topAlbum.append(e['albumImage']['value'])
                    topAlbum.append(e['albumPlayCount']['value'])
                    self.topAlbums.append(topAlbum)

                self.topAlbums = self.topAlbums[:self.max_items]
            # else:
            #     print("Not enough albums to display. Fetching from API...")
            #     self.fetchTopAlbums()

            # Obter top tracks
            query = """
                        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                        PREFIX cs: <http://www.xpand.com/rdf/>
                        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                        SELECT ?trackName ?trackImage ?trackPlayCount ?artistName
                        WHERE{
                            ?track rdf:type cs:Track .
                            ?track cs:Tag <%s> .
                            ?track foaf:name ?trackName .
                            ?track foaf:Image ?trackImage .
                            ?track cs:playCount ?trackPlayCount .
                            ?track cs:MusicArtist ?artist .
                            ?artist foaf:name ?artistName .
                        }
                        ORDER BY DESC(xsd:integer(?trackPlayCount))
                    """ % (tagURI)

            payload_query = {"query": query}
            res = accessor.sparql_select(body=payload_query,
                                         repo_name=repo_name)
            res = json.loads(res)

            if len(res['results']['bindings']) > 0:
                for e in res['results']['bindings']:
                    topTrack = []

                    topTrack.append(unquote(e['artistName']['value']))
                    topTrack.append(unquote(e['trackName']['value']))
                    topTrack.append(e['trackImage']['value'])
                    topTrack.append(e['trackPlayCount']['value'])
                    self.topTracks.append(topTrack)

                self.topTracks = self.topTracks[:self.max_items]
            # else:
            #     print("Not enough tracks to display. Fetching from API...")
            #     self.fetchTopTracks()


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

            self.fetchTopTracks()
            self.fetchTopArtists()
            self.fetchTopAlbums()

    def fetchTopTracks(self):
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

    def fetchTopArtists(self):
        url = urlopen( getTagTopArtistsURL(quote(self.name), self.max_items) )
        tree = ET.parse(url)
        root = tree.getroot()

        for x in root.findall('topartists/artist'):
            artistMBID = None
            artistInfo = []

            artist = x.find('name').text

            # if x.findall('mbid'):
            #     artistMBID = x.find('mbid').text

            if x.findall('.//image[@size="mega"]'):
                artistImage = x.find('.//image[@size="mega"]').text
            else:
                artistImage = self.noArtistImage

            artistInfo.append(artist)

            # if artistMBID:
            #     artistInfo.append(artistMBID)

            artistInfo.append(artistImage)
            self.topArtists.append(artistInfo)

    def fetchTopAlbums(self):
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