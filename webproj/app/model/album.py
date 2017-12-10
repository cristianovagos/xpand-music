import os, html, json, rdflib, lxml.etree as ETree
import xml.etree.ElementTree as ET
from urllib.parse import quote, unquote, urlparse
from urllib.request import urlopen
from urllib.error import HTTPError
from ..model.artist import Artist
from ..model.tag import Tag
from ..api.urls import getAlbumInfoURL, getAlbumInfoIDURL, getTrackInfoURL
from ..db.BaseXClient import Session
from ..utils.dates import calculateAge
from datetime import datetime
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient
from collections import Counter
from wikidata.client import Client

# dados de ligação ao GraphDB
ENDPOINT = "http://localhost:7200"
REPO_NAME = "xpand-music"

class Album:

    def __init__(self, name, artist, mbid=None, max_items=5):
        self.name = name
        self.artist = artist
        self.mbid = mbid
        self.max_items = max_items
        self.image = None
        self.tracks = []
        self.tags = []
        self.comments = []
        self.wikiTextShort = None
        self.wikiTextFull = None
        self.similarAlbums = []
        self.recorders = []
        self.genres = []
        self.producer = None
        self.previousAlbum = None
        self.nextAlbum = None
        self.datePublished = None
        self.age = None

        self.noAlbumImage = self.noTrackImage = "https://www.shareicon.net/data/2015/07/09/66681_music_512x512.png"
        self.noWikiText = "Sorry, no wiki available for this album."

        self.wikiData = False
        self.albumExists = True

        # if (self.checkDatabase()):
        #     print('Fetching from database')
        #     self.fetchInfoDatabase()
        # else:
        #     print('Fetching from API')
        #     # self.fetchInfo()
        #     # self.putInDatabase()
        #     self.transformAlbum()

        if self.checkGraphDB():
            print('Fetching ', self.name,' from GraphDB')
            self.fetchInfoGraphDB()
        else:
            print('Fetching ', self.name,' from API')
            self.transformAlbumRDF()

    def checkGraphDB(self):
        client = ApiClient(endpoint=ENDPOINT)
        accessor = GraphDBApi(client)

        query = """
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                    PREFIX cs: <http://www.xpand.com/rdf/>
                    SELECT *
                    WHERE{
                        ?artist rdf:type cs:MusicArtist .
                        ?artist foaf:name "%s" .
                        ?album rdf:type cs:Album .
                        ?album cs:MusicArtist ?artist .
                        ?album foaf:name "%s" .
                    }
                """ % (quote(self.artist), quote(self.name))

        payload_query = {"query": query}
        res = accessor.sparql_select(body=payload_query,
                                     repo_name=REPO_NAME)
        res = json.loads(res)

        for e in res['results']['bindings']:
            if (e['album']['value']):
                return True
            return False

    def getAlbumURI(self, albumName):
        client = ApiClient(endpoint=ENDPOINT)
        accessor = GraphDBApi(client)

        query = """
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                    PREFIX cs: <http://www.xpand.com/rdf/>
                    SELECT *
                    WHERE{
                        ?artist rdf:type cs:MusicArtist .
                        ?artist foaf:name "%s" .
                        ?album rdf:type cs:Album .
                        ?album cs:MusicArtist ?artist .
                        ?album foaf:name "%s" .
                    }
                """ % (quote(self.artist), quote(albumName))

        payload_query = {"query": query}
        res = accessor.sparql_select(body=payload_query,
                                     repo_name=REPO_NAME)
        res = json.loads(res)

        for e in res['results']['bindings']:
            return e['album']['value']

    def checkTrackGraphDB(self, trackName):
        client = ApiClient(endpoint=ENDPOINT)
        accessor = GraphDBApi(client)

        query = """
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                    PREFIX cs: <http://www.xpand.com/rdf/>
                    SELECT *
                    WHERE{
                        ?artist rdf:type cs:MusicArtist .
                        ?artist foaf:name "%s" .
                        ?track rdf:type cs:Track .
                        ?track cs:MusicArtist ?artist .
                        ?track foaf:name "%s" .
                        ?track cs:playCount ?trackCount .
                    }
                """ % (quote(self.artist), trackName)

        payload_query = {"query": query}
        res = accessor.sparql_select(body=payload_query,
                                     repo_name=REPO_NAME)
        res = json.loads(res)

        for e in res['results']['bindings']:
            if (e['track']['value']):
                return True
            return False

    def transformAlbumRDF(self):
        print("Transforming Album (RDF)...")

        try:
            url = urlopen(getAlbumInfoURL(quote(self.artist), quote(self.name)))
        except HTTPError:
            print('Album doesn\'t exist!')
            self.artistExists = False
        else:
            currentPath = os.getcwd()

            # Transformacao do artista
            xmlParsed = ETree.parse(url)

            albumXSLT = ETree.parse(open(currentPath + '/app/xml/transformAlbumRDF.xsl', 'r'))
            transform = ETree.XSLT(albumXSLT)
            finalAlbum = transform(xmlParsed)

            finalAlbum = str.replace(str(finalAlbum), '<?xml version="1.0"?>', '')

            g = rdflib.Graph()
            g.parse(data=finalAlbum, format="application/rdf+xml")

            client = ApiClient(endpoint=ENDPOINT)
            accessor = GraphDBApi(client)

            print("Inserting album into GraphDB...")

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
                                             repo_name=REPO_NAME)

            # Retirar dados da WikiData
            self.fetchWikiData()

            # Verificar inferencias
            self.checkInferences()

            # Retirar dados do GraphDB e preencher atributos da classe
            self.fetchInfoGraphDB()

    def fetchInfoGraphDB(self):
        client = ApiClient(endpoint=ENDPOINT)
        accessor = GraphDBApi(client)

        query = """
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX cs: <http://www.xpand.com/rdf/>
                    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                    SELECT ?imagem ?tagName ?biografia
                    WHERE{
                        ?album rdf:type cs:Album .
                        ?album foaf:name "%s" .
                        ?album foaf:Image ?imagem .
                        ?album cs:Tag ?tag .
                        ?album cs:biography ?biografia .
                        ?tag foaf:name ?tagName .
                    }
                """ % (quote(self.name))

        payload_query = {"query": query}
        res = accessor.sparql_select(body=payload_query,
                                     repo_name=REPO_NAME)
        res = json.loads(res)

        for e in res['results']['bindings']:
            self.image = e['imagem']['value']
            Tag(unquote(e['tagName']['value']), displayTop=False)
            self.tags.append(unquote(e['tagName']['value']))
            self.wikiTextShort = unquote(e['biografia']['value'])

        # outra query para as tracks

        query = """
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX cs: <http://www.xpand.com/rdf/>
                    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                    SELECT ?trackname
                    WHERE{
                        ?album rdf:type cs:Album .
                        ?album foaf:name "%s" .
                        ?track cs:Album ?album .
                        ?track foaf:name ?trackname .
                    }
                """ % (quote(self.name))

        payload_query = {"query": query}
        res = accessor.sparql_select(body=payload_query,
                                     repo_name=REPO_NAME)
        res = json.loads(res)

        for e in res['results']['bindings']:
            self.tracks.append(unquote(e['trackname']['value']))

            # Inserir Track no GraphDB
            self.transformTrackRDF(e['trackname']['value'])


        # Similar Albums
        query = """
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX cs: <http://www.xpand.com/rdf/>
                    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                    SELECT ?similarName ?similarImage ?similarArtist
                    WHERE{
                        ?album rdf:type cs:Album .
                        ?album foaf:name "%s" .
                        ?similar cs:similarAlbum ?album .
                        ?similar foaf:name ?similarName .
                        ?similar foaf:Image ?similarImage .
                        ?similar cs:MusicArtist ?artist .
                        ?artist foaf:name ?similarArtist .
                    }
                """ % (quote(self.name))

        payload_query = {"query": query}
        res = accessor.sparql_select(body=payload_query,
                                     repo_name=REPO_NAME)
        res = json.loads(res)

        for e in res['results']['bindings']:
            if unquote(e['similarArtist']['value']) == self.artist:
                break

            similarInfo = []

            similarInfo.append(unquote(e['similarName']['value']))
            similarInfo.append(e['similarImage']['value'])
            similarInfo.append(unquote(e['similarArtist']['value']))

            self.similarAlbums.append(similarInfo)

        self.similarAlbums = self.similarAlbums[:self.max_items]

        # WikiData Info
        query = """
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX cs: <http://www.xpand.com/rdf/>
                    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                    SELECT *
                    WHERE{
                        ?album rdf:type cs:Album .
                        ?album foaf:name "%s" .
                        OPTIONAL {
                            ?album cs:recorder ?recorder .
                        }
                        OPTIONAL {
                            ?album cs:genre ?genre .
                        }
                        OPTIONAL {
                            ?album cs:datePublished ?datePublished .
                        }
                        OPTIONAL {
                            ?album cs:producer ?producer .
                        }
                        OPTIONAL {
                            ?album cs:previousAlbum ?previousAlbum .
                        }
                        OPTIONAL {
                            ?album cs:nextAlbum ?nextAlbum .
                        }
                    }
                """ % (quote(self.name))

        payload_query = {"query": query}
        res = accessor.sparql_select(body=payload_query,
                                     repo_name=REPO_NAME)
        res = json.loads(res)

        for e in res['results']['bindings']:
            try:
                self.recorders.append(unquote(e['recorder']['value']))
            except Exception:
                self.recorders = None

            try:
                self.genres.append(unquote(e['genre']['value']).capitalize())
            except Exception:
                self.genres = None

            try:
                self.producer = unquote(e['producer']['value'])
            except Exception:
                self.producer = None

            try:
                self.previousAlbum = unquote(e['previousAlbum']['value'])
            except Exception:
                self.previousAlbum = None

            try:
                self.nextAlbum = unquote(e['nextAlbum']['value'])
            except Exception:
                self.nextAlbum = None

            try:
                tmpDate = datetime.strptime(unquote(e['datePublished']['value']), '%Y-%m-%d')
                self.datePublished = tmpDate.strftime('%d/%m/%Y')
                self.age = calculateAge(tmpDate)
            except Exception:
                self.datePublished = None
                self.age = None

        if self.recorders:
            self.recorders = list(set(self.recorders))
        if self.genres:
            self.genres = list(set(self.genres))


    def checkInferences(self):
        # Inferencia Albuns Semelhantes
        # Consideram-se semelhantes albuns que tenham pelo menos 3 tags em comum

        # ligar ao GraphDB
        client = ApiClient(endpoint=ENDPOINT)
        accessor = GraphDBApi(client)

        # obter albuns com as mesmas tags que este album
        query = """
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                    PREFIX cs: <http://www.xpand.com/rdf/>
                    SELECT ?album1 ?album2 ?album2Name
                    WHERE{
                        ?album1 rdf:type cs:Album .
                        ?album1 foaf:name "%s" .
                        ?album1 cs:Tag ?tag .
                        ?album2 rdf:type cs:Album .
                        ?album2 cs:Tag ?tag .
                        ?album2 foaf:name ?album2Name
                    }
                """ % (quote(self.name))

        payload_query = {"query": query}
        res = accessor.sparql_select(body=payload_query,
                                     repo_name=REPO_NAME)
        res = json.loads(res)

        albumsWithSameTags = []

        for e in res['results']['bindings']:
            # obter uri do album atual
            uriAlbum = e['album1']['value']

            # se album diferente do atual, guardar
            if(e['album2Name']['value'] != quote(self.name)):
                albumsWithSameTags.append(e['album2']['value'])

        # contar numero de ocorrencias de cada album
        auxCount = Counter(albumsWithSameTags)

        # para cada album se o numero de ocorrencia
        # de tags for maior ou igual a 3 é album semelhante
        for album in auxCount:
            if auxCount.get(album) >= 3:
                # album1 é semelhante ao 2
                # album2 é semelhante ao 1
                query = """
                            PREFIX cs: <http://www.xpand.com/rdf/>
                            INSERT DATA
                            { 
                                <%s> cs:similarAlbum <%s> . 
                                <%s> cs:similarAlbum <%s> .
                            }
                        """ % (album, uriAlbum, uriAlbum, album)

                # Enviar a query via API do GraphDB
                payload_query = {"update": query}
                res = accessor.sparql_update(body=payload_query,
                                             repo_name=REPO_NAME)

        # Se não houver dados da wikiData não vale a pena continuar
        if not self.wikiData:
            return


    def fetchWikiData(self):
        # Objetivo: obter ID do album na Wikidata via JSON
        url = urlopen(
            "https://en.wikipedia.org/w/api.php?action=query&prop=pageprops&ppprop=wikibase_item&redirects=1&titles=" + quote(
                self.name) + "&format=json")

        # Obter o JSON
        data = json.loads(url.read().decode("utf-8"))
        item = None
        tmp = dict(data['query']['pages'])
        for key, value in tmp.items():
            # Percorrer o JSON para obter o wikibase_item que é o ID da Wikidata
            try:
                item = value['pageprops']['wikibase_item']
            except Exception:
                # Caso o artista a procurar não exista na Wikidata, ou erro na procura
                item = None

        # Verificar se temos ID
        if not item:
            print("Failed to fetch data from Wikidata. The page seems invalid.")
            return

        print("Trying to fetch data from Wikidata...")

        # Criar cliente que se liga à Wikidata
        client = Client()

        # Obter o item a partir da Wikidata
        entity = client.get(item, load=True)

        albumFound = False

        # Saber se é album
        instanceProperty = client.get('P31')
        for list in entity.getlist(instanceProperty):
            if str(list.label) == "album":
                print("Album detected")
                albumFound = True

        if not albumFound:
            print("Album not found in Wikidata.")
            return

        # Verificar se o artista
        performerProperty = client.get('P175')
        try:
            performer = str(entity[performerProperty].label)
        except Exception:
            performer = None

        if performer not in self.artist:
            print("Could not get data from Wikidata: performer not the same as this artist!")
            return

        print("Fetching data from Wikidata...")

        # Obter editora(s) do album
        recorders = []
        recordProperty = client.get('P264')
        try:
            for records in entity.getlist(recordProperty):
                recorders.append(str(records.label))
        except Exception:
            recorders = None

        # Obter estilo(s) musical do album
        genres = []
        genreProperty = client.get('P136')
        try:
            for genre in entity.getlist(genreProperty):
                genres.append(str(genre.label))
        except Exception:
            genres = None

        # Obter data de lançamento do álbum
        publishDateProperty = client.get('P577')
        try:
            publishDate = str(entity[publishDateProperty])
        except Exception:
            publishDate = None

        # Obter produtor do álbum
        producerProperty = client.get('P162')
        try:
            producer = str(entity[producerProperty].label)
        except Exception:
            producer = None

        # Obter álbum anterior
        previousAlbumProperty = client.get('P155')
        try:
            previousAlbum = str(entity[previousAlbumProperty].label)
        except Exception:
            previousAlbum = None

        # Obter próximo álbum
        nextAlbumProperty = client.get('P156')
        try:
            nextAlbum = str(entity[nextAlbumProperty].label)
        except Exception:
            nextAlbum = None

        # ligar ao GraphDB
        client = ApiClient(endpoint=ENDPOINT)
        accessor = GraphDBApi(client)

        albumURI = self.getAlbumURI(self.name)

        query = """
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                    PREFIX cs: <http://www.xpand.com/rdf/>
                    INSERT DATA {
                        <%s> cs:WikiData true .
                """ % (albumURI)

        if (recorders):
            for i in recorders:
                query += """
                                <%s> cs:recorder "%s" .
                        """ % (albumURI, quote(i))

        if (genres):
            for i in genres:
                query += """
                                <%s> cs:genre "%s" .
                        """ % (albumURI, quote(i))

        if (publishDate):
            query += """
                                <%s> cs:datePublished "%s" .
                        """ % (albumURI, quote(publishDate))
            
        if (producer):
            query += """
                                <%s> cs:producer "%s" .
                        """ % (albumURI, quote(producer))
        
        if (previousAlbum):
            query += """
                                <%s> cs:previousAlbum "%s" .
                        """ % (albumURI, quote(previousAlbum))
            
        if (nextAlbum):
            query += """
                                <%s> cs:nextAlbum "%s" .
                        """ % (albumURI, quote(nextAlbum))

        query += """
                            }
                         """

        # executar query via API do GraphDB
        payload_query = {"update": query}
        res = accessor.sparql_update(body=payload_query,
                                     repo_name=REPO_NAME)

        self.wikiData = True


    def transformTrackRDF(self, trackName):
        # Verificar se a musica ja existe no grafo
        if self.checkTrackGraphDB(trackName):
            return

        print("Transforming Track ", unquote(trackName), "...")

        try:
            url = urlopen(getTrackInfoURL(trackName, quote(self.artist)))
            print(getTrackInfoURL(trackName, quote(self.artist)))
        except HTTPError:
            print('Track doesn\'t exist!')
        else:
            currentPath = os.getcwd()

            # Transformacao do artista
            xmlParsed = ETree.parse(url)

            trackXSLT = ETree.parse(open(currentPath + '/app/xml/transformTrackRDF.xsl', 'r'))
            transform = ETree.XSLT(trackXSLT)
            finalTrack = transform(xmlParsed)

            finalTrack = str.replace(str(finalTrack), '<?xml version="1.0"?>', '')

            g = rdflib.Graph()
            g.parse(data=finalTrack, format="application/rdf+xml")

            client = ApiClient(endpoint=ENDPOINT)
            accessor = GraphDBApi(client)

            print("Inserting track into GraphDB...")

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
                                             repo_name=REPO_NAME)


    def transformAlbum(self):
        print("Transforming Album ", self.name, "...")
        try:
            url = urlopen(getAlbumInfoURL(quote(self.artist), quote(self.name)))
        except HTTPError:
            print('Album doesn\'t exist!')
            self.albumExists = False
        else:
            currentPath = os.getcwd()

            # Obtencao do XML Schema
            xmlSchemaAlbum_doc = ETree.parse(open(currentPath + '/app/xml/schAlbum.xsd', 'r'))
            xmlSchemaAlbum_doc = ETree.XMLSchema(xmlSchemaAlbum_doc)

            # Transformacao do album
            xmlParsed = ETree.parse(url)
            albumXSLT = ETree.parse(open(currentPath + '/app/xml/transformAlbum.xsl', 'r'))
            transform = ETree.XSLT(albumXSLT)
            finalAlbum = transform(xmlParsed)

            finalAlbum = str.replace(str(finalAlbum), '<?xml version="1.0"?>', '')

            if xmlSchemaAlbum_doc.validate(ETree.fromstring(finalAlbum)):
                print("Album is valid!")
                print("Inserting album in database...")

                #preparar para inserir na bd
                session = Session('localhost', 1984, 'admin', 'admin')

                try:
                    query = "let $artists := collection('xpand-db')//artist " + \
                            "let $albums := $artists[name='" + self.artist + "']/albums " + \
                            "let $node := " + str(finalAlbum) + " " + \
                            "return insert node $node into $albums "

                    queryObj = session.query(query)

                    queryObj.execute()

                    queryObj.close()

                except Exception as e:
                    print("Something failed on XML Database!")
                    print(e)

                finally:
                    print("Completed.")
                    if session:
                        session.close()
                    self.fetchInfoDatabase()

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
            print(e)
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
            print(e)
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
            print(e)
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

    def getSimilarAlbums(self):
        return self.similarAlbums

    def getRecorders(self):
        return self.recorders

    def getGenres(self):
        return self.genres

    def getProducer(self):
        return self.producer

    def getPreviousAlbum(self):
        return self.previousAlbum

    def getNextAlbum(self):
        return self.nextAlbum

    def getDatePublished(self):
        return self.datePublished

    def getAge(self):
        return self.age

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