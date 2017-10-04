# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpRequest
from django.http import HttpResponse
from datetime import datetime
import xml.etree.ElementTree as ET
from urllib.request import urlopen


# Create your views here.

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    tparams = {
        'title':'xPand',
        'message':'Your indexx page.',
        'year':datetime.now().year,
    }
    return render(request, 'index.html', tparams)

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    tparams = {
        'title':'Contact',
        'message':'Your contact page.',
        'year':datetime.now().year,
    }
    return render(request, 'contact.html', tparams)


def about(request):
    assert isinstance(request, HttpRequest)
    tparams = {
        'title': 'About',
        'message': 'Your application description page.',
        'year': datetime.now().year,
    }
    return render(
        request,
        'about.html',
        {
            'title': 'About',
            'message': 'Your application description page.',
            'year': datetime.now().year,
        }
    )

                                                ### criadas ###
# top musicas atualmente tag = rap,  esta static ainda   &tag= ...
def top(request):
    """Renders the list page."""
    assert isinstance(request, HttpRequest)

    file = urlopen(
        "http://ws.audioscrobbler.com/2.0/?method=tag.gettopalbums&tag=rap&api_key=32f8947b156b3993b3ff9159b81f4667")
    tree = ET.parse(file)
    root = tree.getroot()
    result = []

    for x in root.findall('albums'):
        for y in x.findall('album'):
            aux = []
            nomeAlbum = y.find('name').text
            for ar in y.findall('artist'):
                nomeArtista = ar.find('name').text
                mbid = ar.find('mbid').text
                aux.append(nomeAlbum)
                aux.append(nomeArtista)
                aux.append(mbid)
            img = y.find('.//image[@size="large"]').text
            aux.append(img)
            result.append(aux)

    tparams = {
        'title':'TOP Categorias',
        'year':datetime.now().year,
        'array' :result,
    }
    return render(request, 'top.html', tparams)




def albumInfo(request, album, artist):


    assert isinstance(request, HttpRequest)

    file = urlopen(
        "http://ws.audioscrobbler.com/2.0/?method=album.getinfo&api_key=32f8947b156b3993b3ff9159b81f4667&artist=" + str(artist) + "&album=" + str(album) + "")
    tree = ET.parse(file)
    root = tree.getroot()
    result = {}
    tracks = []
    for x in root.findall('album'):
        album = x.find('name').text
        artist = x.find('artist').text
        listeners = x.find('listeners').text
        playcount = x.find('playcount').text
        image = x.find('.//image[@size="mega"]').text
        for y in x.findall('tracks/track'):  # tracks
            track=[]
            track.append(y.find('name').text)
            dur = int(y.find('duration').text)/100
            track.append(dur)
            tracks.append(track)

    tparams = {
        'album': album,
        'artist':artist,
        'year': datetime.now().year,
        'image': image,
        'listeners' : listeners,
        'playcount' : playcount,
        'dict': tracks,
        'title': album,
    }
    return render(request, 'albumInfo.html', tparams)


def artistInfo(request, artist):
    # funcao que retorna a informacao sobre o artista e respectivos artistas semelhantes
    # artist= "Eminem"


    assert isinstance(request, HttpRequest)
    file = urlopen(
        "http://ws.audioscrobbler.com/2.0/?method=artist.getinfo&artist="+str(artist)+"&api_key=32f8947b156b3993b3ff9159b81f4667")
    tree = ET.parse(file)
    root = tree.getroot()
    similars = []
    bio = []
    for x in root.findall('artist'):
        bio.append(x.find('bio/summary').text)
        bio.append(x.find('bio/content').text)
        bio.append(x.find('.//image[@size="mega"]').text)
        bio.append(x.find('name').text)
        for y in x.findall('similar/artist'):
            similar = []
            similar.append(y.find('name').text)
            similar.append(y.find('.//image[@size="mega"]').text)
            similars.append(similar)

    topAlbums=getAlbums(artist)
    top5 = topAlbums[:5]

    topSongs=getSongs(artist)
    songs5=topSongs[:5]

    tparams = {
        'summary' : bio[0],    # bio, sumario
        'content' : bio[1],    # bio, texto completo
        'image'   : bio[2],    # imagem artista
        'name'    : bio[3],    # nome artista
        'similars': similars,  # 0- name artists, 1- image
        'topAlbums': topAlbums, # array de top albums
        'top5': top5,
        'songs5':songs5,
        'title' : bio[3],
    }
    return render(request, 'artistInfo.html', tparams)


def getAlbums(artista):

    file = urlopen(
        "http://ws.audioscrobbler.com/2.0/?method=artist.gettopalbums&artist=" + str(artista) + "&api_key=32f8947b156b3993b3ff9159b81f4667")
    tree = ET.parse(file)
    root = tree.getroot()
    result = []

    for x in root.findall('topalbums/album'):
        aux = []
        aux.append(str(x.find('name').text))
        aux.append(x.find('image[@size="extralarge"]').text)
        result.append(aux)

    return result

def getSongs(artista):
    file = urlopen(
        "http://ws.audioscrobbler.com/2.0/?method=artist.gettoptracks&artist=" + artista + "&api_key=32f8947b156b3993b3ff9159b81f4667")
    tree = ET.parse(file)
    root = tree.getroot()
    result = []

    for x in root.findall('toptracks/track'):
        aux = []
        aux.append(x.find('name').text)
        aux.append(x.find('image[@size="extralarge"]').text)
        result.append(aux)

    return result