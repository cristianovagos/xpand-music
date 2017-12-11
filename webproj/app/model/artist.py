import html, os, json, rdflib, lxml.etree as ETree
import xml.etree.ElementTree as ET
from urllib.parse import quote, unquote, urlparse
from urllib.request import urlopen
from urllib.error import HTTPError
from ..api.urls import getArtistInfoURL, getArtistTopAlbumsIDURL, \
    getArtistTopTracksIDURL, getArtistTopAlbumsURL, getArtistTopTracksURL
from ..db.BaseXClient import Session
from ..model.tag import Tag
from ..utils.countries import getISOCode
from ..utils.dates import calculateAge
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient
from collections import Counter
from datetime import datetime
from wikidata.client import Client


# dados de ligação ao GraphDB
ENDPOINT = "http://localhost:7200"
REPO_NAME = "xpand-music"

class Artist:

    def __init__(self, name, max_items=5, store=True):
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
        self.members = []
        self.occupation = []
        self.recorders = []
        self.genres = []
        self.website = None
        self.gender = None
        self.country = None
        self.givenName = None
        self.birthDate = None
        self.age = None
        self.yearFounded = None
        self.band = False
        self.bands = []
        self.wikiData = False

        self.max_items = max_items

        self.noArtistImage = "http://paradeal.pp.ua/img/no-user.jpg"
        self.noAlbumImage = self.noTrackImage = "https://www.shareicon.net/data/2015/07/09/66681_music_512x512.png"
        self.noBioText = "Artist Biography not available, sorry."

        self.artistExists = True

        # if self.checkDatabase():
        #     print('Fetching from database')
        #     self.fetchInfoDatabase()
        # else:
        #     print('Fetching from API')
        #     #self.fetchInfo()
        #     #if store:
        #     #self.putInDatabase()
        #     self.transformArtist()

        if self.checkGraphDB():
            print('Fetching from GraphDB')
            self.fetchInfoGraphDB()
        else:
            print('Fetching from API')
            self.transformArtistRDF()


    def fetchInfoGraphDB(self):
        client = ApiClient(endpoint=ENDPOINT)
        accessor = GraphDBApi(client)

        query = """
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX cs: <http://www.xpand.com/rdf/>
                    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                    SELECT ?imagem ?tagName ?biografia
                    WHERE{
                        ?artista rdf:type cs:MusicArtist .
                        ?artista foaf:name "%s" .
                        ?artista foaf:Image ?imagem .
                        ?artista cs:Tag ?tag .
                        ?artista cs:biography ?biografia .
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
            self.biographyShort = unquote(e['biografia']['value'])

        # fazer outra query para os albuns
        query = """
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX cs: <http://www.xpand.com/rdf/>
                    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                    SELECT ?albumName ?albumCover ?albumPlayCount
                    WHERE{
                        ?artista rdf:type cs:MusicArtist .
                        ?artista foaf:name "%s" .
                        ?album rdf:type cs:Album .
                        ?album cs:MusicArtist ?artista .
                        ?album foaf:name ?albumName .
                        ?album foaf:Image ?albumCover .
                        ?album cs:playCount ?albumPlayCount .
                    }
                    ORDER BY DESC(xsd:integer(?albumPlayCount))
                """ % (quote(self.name))

        payload_query = {"query": query}
        res = accessor.sparql_select(body=payload_query,
                                     repo_name=REPO_NAME)
        res = json.loads(res)

        for e in res['results']['bindings']:
            albumInfo = []

            albumInfo.append(unquote(e['albumName']['value']))
            albumInfo.append(e['albumCover']['value'])
            albumInfo.append(e['albumPlayCount']['value'])

            if albumInfo not in self.topAlbums:
                self.topAlbums.append(albumInfo)

        # so ficar com o numero de albuns mais ouvidos
        self.topAlbums = self.topAlbums[:self.max_items]

        # Tracks
        query = """
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX cs: <http://www.xpand.com/rdf/>
                    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                    SELECT ?trackName ?trackCover ?trackPlayCount
                    WHERE{
                        ?artista rdf:type cs:MusicArtist .
                        ?artista foaf:name "%s" .
                        ?track rdf:type cs:Track .
                        ?track cs:MusicArtist ?artista .
                        ?track foaf:name ?trackName .
                        ?track cs:playCount ?trackPlayCount .
                        ?album rdf:type cs:Album .
                        ?album cs:MusicArtist ?artista .
                        ?track cs:Album ?album .
                        ?album foaf:Image ?trackCover .
                    }
                    ORDER BY DESC(xsd:integer(?trackPlayCount))
                """ % (quote(self.name))

        payload_query = {"query": query}
        res = accessor.sparql_select(body=payload_query,
                                     repo_name=REPO_NAME)
        res = json.loads(res)

        for e in res['results']['bindings']:
            trackInfo = []

            trackInfo.append(unquote(e['trackName']['value']))
            trackInfo.append(e['trackCover']['value'])
            trackInfo.append(e['trackPlayCount']['value'])

            self.topTracks.append(trackInfo)

        # so ficar com o numero de tracks mais ouvidas
        self.topTracks = self.topTracks[:self.max_items]

        # Similar Artists
        query = """
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX cs: <http://www.xpand.com/rdf/>
                    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                    SELECT ?similarName ?similarImage
                    WHERE{
                        ?artista rdf:type cs:MusicArtist .
                        ?artista foaf:name "%s" .
                        ?similar cs:similarArtist ?artista .
                        ?similar foaf:name ?similarName .
                        ?similar foaf:Image ?similarImage .
                    }
                """ % (quote(self.name))

        payload_query = {"query": query}
        res = accessor.sparql_select(body=payload_query,
                                     repo_name=REPO_NAME)
        res = json.loads(res)

        for e in res['results']['bindings']:
            similarInfo = []

            similarInfo.append(unquote(e['similarName']['value']))
            similarInfo.append(e['similarImage']['value'])

            self.similarArtists.append(similarInfo)

        self.similarArtists = self.similarArtists[:self.max_items]

        # WikiData Info
        query = """
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX cs: <http://www.xpand.com/rdf/>
                    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                    SELECT *
                    WHERE{
                        ?artista rdf:type cs:MusicArtist .
                        ?artista foaf:name "%s" .
                        OPTIONAL {
                            ?artista cs:bandMember ?member .
                        }
                        OPTIONAL {
                            ?artista foaf:gender ?gender .
                        }
                        OPTIONAL {
                            ?artista cs:occupation ?occupation .
                        }
                        OPTIONAL {
                            ?artista cs:recorder ?recorder .
                        }
                        OPTIONAL {
                            ?artista cs:genre ?genre .
                        }
                        OPTIONAL {
                            ?artista cs:website ?website .
                        }
                        OPTIONAL {
                            ?artista cs:country ?country .
                        }
                        OPTIONAL {
                            ?artista foaf:givenName ?givenName .
                        }
                        OPTIONAL {
                            ?artista cs:birthDate ?birthDate .
                        }
                        OPTIONAL {
                            ?artista cs:yearFounded ?yearFounded .
                        }
                        OPTIONAL {
                            ?artista cs:isMember ?band .
                            ?band foaf:name ?bandName .
                        }
                    }
                """ % (quote(self.name))

        payload_query = {"query": query}
        res = accessor.sparql_select(body=payload_query,
                                     repo_name=REPO_NAME)
        res = json.loads(res)

        for e in res['results']['bindings']:
            try:
                self.bands.append(unquote(e['bandName']['value']))
            except Exception:
                self.bands = None

            try:
                self.members.append(unquote(e['member']['value']))
            except Exception:
                self.members = None

            try:
                self.gender = unquote(e['gender']['value'])
            except Exception:
                self.gender = None

            try:
                self.occupation.append(unquote(e['occupation']['value']).capitalize())
            except Exception:
                self.occupation = None

            try:
                self.recorders.append(unquote(e['recorder']['value']))
            except Exception:
                self.recorders = None

            try:
                self.genres.append(unquote(e['genre']['value']).capitalize())
            except Exception:
                self.genres = None

            try:
                self.website = unquote(e['website']['value'])
            except Exception:
                self.website = None

            try:
                self.country = unquote(e['country']['value'])
            except Exception:
                self.country = None

            try:
                self.givenName = unquote(e['givenName']['value'])
            except Exception:
                self.givenName = None

            try:
                tmpDate = datetime.strptime(unquote(e['birthDate']['value']), '%Y-%m-%d')
                self.birthDate = tmpDate.strftime('%d/%m/%Y')
                self.age = calculateAge(tmpDate)
            except Exception:
                self.birthDate = None
                self.age = None

            try:
                self.yearFounded = unquote(e['yearFounded']['value'])
            except Exception:
                self.yearFounded = None

        if self.members:
            self.members = list(set(self.members))
        if self.occupation:
            self.occupation = list(set(self.occupation))
        if self.recorders:
            self.recorders = list(set(self.recorders))
        if self.genres:
            self.genres = list(set(self.genres))
        if self.bands:
            self.bands = list(set(self.bands))

    def fetchInfoDatabase(self):
        result = False
        session = Session('localhost', 1984, 'admin', 'admin')

        try:
            query = "let $artists := collection('xpand-db')//artist " + \
                    "let $value := $artists[name= '" + self.name + "'] " + \
                    "return <result>{$value}</result>"

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

                    if tag.findall('similar/similarartist'):
                        for artist in tag.findall('similar/similarartist'):
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

                                if comment.findall('id'):
                                    commentInfo.append(comment.find('id').text)

                                self.comments.append(commentInfo)

    # verificar se o artista já existe no GraphDB
    def checkGraphDB(self):
        # ligar ao GraphDB
        client = ApiClient(endpoint=ENDPOINT)
        accessor = GraphDBApi(client)

        query = """
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                    PREFIX cs: <http://www.xpand.com/rdf/>
                    SELECT *
                    WHERE{
                        ?artista rdf:type cs:MusicArtist .
                        ?artista foaf:name "%s" .
                    }
                """ %(quote(self.name))

        # executar query via API do GraphDB
        payload_query = {"query": query}
        res = accessor.sparql_select(body=payload_query,
                                     repo_name=REPO_NAME)
        res = json.loads(res)

        # percorrer resultados da query
        for e in res['results']['bindings']:
            # se há um ?artista de acordo com a query significa que este existe
            if(e['artista']['value']):
                return True
            return False

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
                query += "<similarartist>" + \
                         "<name>" + html.escape(similarArtist[0]) + "</name>" + \
                         "<image>" + similarArtist[1] + "</image>" + \
                         "</similarartist>"

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

    def transformArtistRDF(self):
        print("Transforming Artist (RDF)...")

        try:
            url = urlopen( getArtistInfoURL(quote(self.name)) )
        except HTTPError:
            print('Artist doesn\'t exist!')
            self.artistExists = False
        else:
            # Obter Current Working Directory
            currentPath = os.getcwd()

            # Transformacao do artista para RDF
            xmlParsed = ETree.parse(url)

            artistXSLT = ETree.parse(open(currentPath + '/app/xml/transformArtistRDF.xsl', 'r'))
            transform = ETree.XSLT(artistXSLT)
            finalArtist = transform(xmlParsed)

            finalArtist = str.replace(str(finalArtist), '<?xml version="1.0"?>', '')

            # Criar grafo RDFLib, inserir o RDF/XML decorrente da transformação
            g = rdflib.Graph()
            g.parse(data=finalArtist, format="application/rdf+xml")

            # ligar ao GraphDB
            client = ApiClient(endpoint=ENDPOINT)
            accessor = GraphDBApi(client)

            print("Inserting artist into GraphDB...")

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
                                             repo_name=REPO_NAME)
                
            # Retirar dados da WikiData
            self.fetchWikiData()

            # Verificar inferencias
            self.checkInferences()

            # Retirar dados do GraphDB e preencher atributos da classe
            self.fetchInfoGraphDB()


    # Retirar dados da Wikidata usando a biblioteca Wikidata
    def fetchWikiData(self):
        # Objetivo: obter ID do artista na Wikidata via JSON
        url = urlopen("https://www.wikidata.org/w/api.php?action=wbsearchentities&search=" + quote(
            self.name) + "&language=en&format=json")

        # Obter o JSON
        data = json.loads(url.read().decode("utf-8"))

        ids = []
        for result in data['search']:
            # Obter todos os IDs
            ids.append(result['id'])

        client = Client()
        entity = None
        occupation = None
        musician = False

        if ids:
            # Percorrer todos os IDs para sabermos quais deles são relacionados com música
            # banda / humano
            for id in ids:
                entity = client.get(id, load=True)

                instanceProperty = client.get('P31')
                try:
                    instance = entity[instanceProperty].label
                except Exception:
                    instance = None

                if str(instance) == 'band':
                    print("Band detected")
                    self.band = True
                    break
                elif str(instance) == 'human':
                    print("Human detected")

                    # Vamos saber se esta pessoa tem algo a ver com musica

                    # Saber ocupação
                    occupation = []
                    occupationProperty = client.get('P106')
                    try:
                        for occup in entity.getlist(occupationProperty):
                            occupation.append(str(occup.label))
                    except Exception:
                        occupation = None

                    if 'singer' in occupation or 'singer-songwriter' in occupation \
                        or 'composer' in occupation or 'musician' in occupation \
                        or 'songwriter' in occupation or 'rapper' in occupation:
                        musician = True
                        break

        if not (musician or self.band):
            print("Could not fetch data from Wikidata.")
            return

        print("Fetching data from Wikidata...")

        # Obter editora(s) do artista
        recorders = []
        recordProperty = client.get('P264')
        try:
            for records in entity.getlist(recordProperty):
                recorders.append(str(records.label))
        except Exception:
            recorders = None

        # Obter estilo(s) musical do artista
        genres = []
        genreProperty = client.get('P136')
        try:
            for genre in entity.getlist(genreProperty):
                genres.append(str(genre.label))
        except Exception:
            genres = None

        websiteProperty = client.get('P856')
        try:
            website = str(entity[websiteProperty])
        except Exception:
            website = None

        bandMembers = gender = birthName = birthDate = year = None

        if not self.band:
            # Sexo
            genderProperty = client.get('P21')
            try:
                gender = str(entity[genderProperty].label)
            except Exception:
                gender = None

            # País
            countryProperty = client.get('P27')
            try:
                country = str(entity[countryProperty].label)
            except Exception:
                country = None

            # Nome de Nascimento
            birthNameProperty = client.get('P1477')
            try:
                birthName = str(entity[birthNameProperty].label)
            except Exception:
                birthName = None

            # Data de Nascimento
            birthDateProperty = client.get('P569')
            try:
                birthDate = str(entity[birthDateProperty])
            except Exception:
                birthDate = None

        else:
            # País de origem da banda
            countryProperty = client.get('P495')
            try:
                country = str(entity[countryProperty].label)
            except Exception:
                country = None

            # Ano de criação da banda
            yearProperty = client.get('P571')
            try:
                year = str(entity[yearProperty].year)
            except Exception:
                year = None

            # Integrantes da banda
            bandMembers = []
            bandMembersProperty = client.get('P527')
            try:
                for member in entity.getlist(bandMembersProperty):
                    bandMembers.append(str(member.label))
            except Exception:
                bandMembers = None

        # ligar ao GraphDB
        client = ApiClient(endpoint=ENDPOINT)
        accessor = GraphDBApi(client)

        artistURI = self.getArtistURI()

        query = """
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                    PREFIX cs: <http://www.xpand.com/rdf/>
                    INSERT DATA {
                        <%s> cs:WikiData true .
                """ % (artistURI)

        if(occupation):
            for i in occupation:
                query += """
                        <%s> cs:occupation "%s" .
                """ % (artistURI, quote(i))

        if (recorders):
            for i in recorders:
                query += """
                        <%s> cs:recorder "%s" .
                """ % (artistURI, quote(i))

        if (genres):
            for i in genres:
                query += """
                        <%s> cs:genre "%s" .
                """ % (artistURI, quote(i))

        if (bandMembers):
            for i in bandMembers:
                query += """
                        <%s> cs:bandMember "%s" .
                """ % (artistURI, quote(i))

        if (website):
                query += """
                        <%s> cs:website "%s" .
                """ % (artistURI, quote(website))

        if (gender):
                query += """
                        <%s> foaf:gender "%s" .
                """ % (artistURI, quote(gender))

        if (country):
                query += """
                        <%s> cs:country "%s" .
                """ % (artistURI, quote(country))

        if (birthName):
                query += """
                        <%s> foaf:givenName "%s" .
                """ % (artistURI, quote(birthName))

        if (birthDate):
                query += """
                        <%s> cs:birthDate "%s" .
                """ % (artistURI, quote(birthDate))

        if (year):
                query += """
                        <%s> cs:yearFounded "%s" .
                """ % (artistURI, quote(year))

        query += """
                    }
                 """

        # executar query via API do GraphDB
        payload_query = {"update": query}
        res = accessor.sparql_update(body=payload_query,
                                     repo_name=REPO_NAME)
        
        self.wikiData = True

    def getArtistURI(self):
        # ligar ao GraphDB
        client = ApiClient(endpoint=ENDPOINT)
        accessor = GraphDBApi(client)

        query = """
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                    PREFIX cs: <http://www.xpand.com/rdf/>
                    SELECT *
                    WHERE{
                        ?artista rdf:type cs:MusicArtist .
                        ?artista foaf:name "%s" .
                    }
                """ % (quote(self.name))

        # executar query via API do GraphDB
        payload_query = {"query": query}
        res = accessor.sparql_select(body=payload_query,
                                     repo_name=REPO_NAME)
        res = json.loads(res)

        # percorrer resultados da query
        for e in res['results']['bindings']:
            return e['artista']['value']

    def checkInferences(self):
        # Inferencia Artistas Semelhantes
        # Consideram-se semelhantes artistas que tenham pelo menos 3 tags em comum

        # ligar ao GraphDB
        client = ApiClient(endpoint=ENDPOINT)
        accessor = GraphDBApi(client)

        # obter artistas com as mesmas tags que este artista
        query = """
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                    PREFIX cs: <http://www.xpand.com/rdf/>
                    SELECT ?artist1 ?artist2 ?artist2Name
                    WHERE{
                        ?artist1 rdf:type cs:MusicArtist .
                        ?artist1 foaf:name "%s" .
                        ?artist1 cs:Tag ?tag .
                        ?artist2 rdf:type cs:MusicArtist .
                        ?artist2 cs:Tag ?tag .
                        ?artist2 foaf:name ?artist2Name
                    }
                """ % (quote(self.name))

        payload_query = {"query": query}
        res = accessor.sparql_select(body=payload_query,
                                     repo_name=REPO_NAME)
        res = json.loads(res)

        artistsWithSameTags = []

        for e in res['results']['bindings']:
            # obter uri do artista atual
            uriArtist = e['artist1']['value']

            # se artista diferente do atual, guardar
            if(e['artist2Name']['value'] != quote(self.name)):
                artistsWithSameTags.append(e['artist2']['value'])

        # contar numero de ocorrencias de cada artista
        auxCount = Counter(artistsWithSameTags)

        # para cada artista se o numero de ocorrencia
        # de tags for maior ou igual a 3 é artista semelhante
        for artist in auxCount:
            if auxCount.get(artist) >= 3:
                # artista1 é semelhante ao 2
                # artista2 é semelhante ao 1
                query = """
                            PREFIX cs: <http://www.xpand.com/rdf/>
                            INSERT DATA
                            { 
                                <%s> cs:similarArtist <%s> . 
                                <%s> cs:similarArtist <%s> .
                            }
                        """ % (artist, uriArtist, uriArtist, artist)

                # Enviar a query via API do GraphDB
                payload_query = {"update": query}
                res = accessor.sparql_update(body=payload_query,
                                             repo_name=REPO_NAME)


        # Se não houver dados da wikiData não vale a pena continuar
        if not self.wikiData:
            return

        # Inferencia membro de uma banda

        # Descobrir URIs de banda/artista
        query = """
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX cs: <http://www.xpand.com/rdf/>
                    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                    SELECT ?band ?artist
                    WHERE{
                        ?band rdf:type cs:MusicArtist .
                        ?band cs:bandMember "%s" .
                        ?artist rdf:type cs:MusicArtist .
                        ?artist foaf:name "%s" .
                    }
                """ % (quote(self.name), quote(self.name))

        payload_query = {"query": query}
        res = accessor.sparql_select(body=payload_query,
                                     repo_name=REPO_NAME)
        res = json.loads(res)

        for e in res['results']['bindings']:
            # obter uris
            uriBand = e['band']['value']
            uriArtist = e['artist']['value']

            query = """
                        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                        PREFIX cs: <http://www.xpand.com/rdf/>
                        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                        INSERT DATA {
                            <%s> cs:isMember <%s> .
                        }
                    """ % (uriArtist, uriBand)

            payload_query = {"update": query}
            res = accessor.sparql_update(body=payload_query,
                                         repo_name=REPO_NAME)



    def transformArtist(self):
        print("Transforming Artist...")

        try:
            url = urlopen( getArtistInfoURL(quote(self.name)) )
        except HTTPError:
            print('Artist doesn\'t exist!')
            self.artistExists = False
        else:
            currentPath = os.getcwd()

            # Obtencao dos XML Schemas
            xmlSchemaArtista_doc = ETree.parse(open(currentPath + '/app/xml/schArtist.xsd', 'r'))
            xmlSchemaArtista_doc = ETree.XMLSchema(xmlSchemaArtista_doc)

            xmlSchemaTopAlb_doc = ETree.parse(open(currentPath + '/app/xml/schTopAlbums.xsd', 'r'))
            xmlSchemaTopAlb_doc = ETree.XMLSchema(xmlSchemaTopAlb_doc)

            xmlSchemaTopTra_doc = ETree.parse(open(currentPath + '/app/xml/schTopTracks.xsd', 'r'))
            xmlSchemaTopTra_doc = ETree.XMLSchema(xmlSchemaTopTra_doc)

            # Transformacao do artista
            xmlParsed = ETree.parse(url)
            artistXSLT = ETree.parse(open(currentPath + '/app/xml/transformArtist.xsl', 'r'))
            transform = ETree.XSLT(artistXSLT)
            finalArtist = transform(xmlParsed)

            finalArtist = str.replace(str(finalArtist), '<?xml version="1.0"?>', '')

            # Transformacao do TopAlbuns
            url = urlopen( getArtistTopAlbumsURL(quote(self.name), self.max_items) )
            xmlParsed = ETree.parse(url)
            topAlbumsXSLT = ETree.parse(open(currentPath + '/app/xml/transformArtistTopAlbums.xsl', 'r'))
            transform = ETree.XSLT(topAlbumsXSLT)
            topAlbums = transform(xmlParsed)

            topAlbums = str.replace(str(topAlbums), '<?xml version="1.0"?>', '')

            # Transformacao das TopTracks
            url = urlopen(getArtistTopTracksURL(quote(self.name), self.max_items))
            xmlParsed = ETree.parse(url)
            topAlbumsXSLT = ETree.parse(open(currentPath + '/app/xml/transformArtistTopTracks.xsl', 'r'))
            transform = ETree.XSLT(topAlbumsXSLT)
            topTracks = transform(xmlParsed)

            topTracks = str.replace(str(topTracks), '<?xml version="1.0"?>', '')


            if xmlSchemaArtista_doc.validate(ETree.fromstring(finalArtist)) \
                and xmlSchemaTopAlb_doc.validate(ETree.fromstring(topAlbums)) \
                and xmlSchemaTopTra_doc.validate(ETree.fromstring(topTracks)):

                print("Artist is valid!")
                print("Inserting artist in database...")

                #preparar para inserir na bd
                session = Session('localhost', 1984, 'admin', 'admin')

                try:
                    query = "let $artists := collection('xpand-db')/artists " + \
                            "let $node := " + str(finalArtist) + " " +\
                            "return insert node $node into $artists "

                    queryObj = session.query(query)

                    queryObj.execute()

                    queryObj.close()

                    query = "let $artists := collection('xpand-db')/artists " + \
                            "let $artist := $artists/artist[name='" + self.name + "']/topAlbums " + \
                            "let $node := " + str(topAlbums) + " " + \
                            "return replace node $artist with $node "

                    queryObj = session.query(query)

                    queryObj.execute()

                    queryObj.close()

                    query = "let $artists := collection('xpand-db')/artists " + \
                            "let $artist := $artists/artist[name='" + self.name + "']/topTracks " + \
                            "let $node := " + str(topTracks) + " " + \
                            "return replace node $artist with $node "

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

    def getMembers(self):
        return self.members

    def getOccupation(self):
        return self.occupation

    def getRecorders(self):
        return self.recorders

    def getGenres(self):
        return self.genres

    def getWebsite(self):
        return self.website

    def getGender(self):
        return self.gender

    def getCountry(self):
        return self.country

    def getCountryCode(self):
        return getISOCode(self.country)

    def getGivenName(self):
        return self.givenName

    def getBirthDate(self):
        return self.birthDate

    def getAge(self):
        return self.age

    def getYearFounded(self):
        return self.yearFounded

    def getBands(self):
        return self.bands

    def isBand(self):
        return self.band

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