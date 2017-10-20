# -*- coding: utf-8 -*-

from datetime import datetime
from urllib.request import urlopen
from .model.artist import Artist
from .model.album import Album
from django.http import HttpRequest
from django.shortcuts import render
from .api.artists.artists import getTopArtists
from .api.tracks.tracks import getTopTracks
from .api.news.news import *

#from webproj.app.api.artists.artists import getArtistInfo


# Create your views here.

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)

    topArtists = getTopArtists()
    topTracks = getTopTracks()

    tparams = {
        'title':'xPand',
        'message':'Your indexx page.',
        'year':datetime.now().year,
        'topArtists' : topArtists,
        'topTracks': topTracks,
        'news': getAllNews(5),
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
#def top(request):
    # """Renders the list page."""
    # assert isinstance(request, HttpRequest)
    #
    # file = urlopen(
    #     "http://ws.audioscrobbler.com/2.0/?method=tag.gettopalbums&tag=rap&api_key=32f8947b156b3993b3ff9159b81f4667")
    # tree = ET.parse(file)
    # root = tree.getroot()
    # result = []
    #
    # for x in root.findall('albums'):
    #     for y in x.findall('album'):
    #         aux = []
    #         nomeAlbum = y.find('name').text
    #         for ar in y.findall('artist'):
    #             nomeArtista = ar.find('name').text
    #             mbid = ar.find('mbid').text
    #             aux.append(nomeAlbum)
    #             aux.append(nomeArtista)
    #             aux.append(mbid)
    #         img = y.find('.//image[@size="large"]').text
    #         aux.append(img)
    #         result.append(aux)
    #
    # tparams = {
    #     'title':'TOP Categorias',
    #     'year':datetime.now().year,
    #     'array' :result,
    # }
    # return render(request, 'top.html', tparams)


def albumInfo(request, album, artist):
    assert isinstance(request, HttpRequest)

    albumObj = Album(str(album), str(artist))
    print(albumObj)

    tparams = {
        'album' : album,
        'artist': artist,
        'year': datetime.now().year,
        'image': albumObj.getImage(),
        'wiki': albumObj.getWikiShort(),
        'tags': albumObj.getTags(),
        'tracks': albumObj.getTracks(),
        'title': album,
    }
    return render(request, 'album.html', tparams)

def artistInfo(request, artist):
    assert isinstance(request, HttpRequest)

    artistObj = Artist(artist)

    tparams = {
        'summary': artistObj.getBiography(True),
        'content': artistObj.getBiography(False),
        'image': artistObj.getImage(),
        'name': artistObj.getName(),
        'similars': artistObj.getSimilarArtists(),
        'topAlbums': artistObj.getTopAlbums(),
        'top5': artistObj.getTopAlbums(),
        'songs5': artistObj.getTopTracks(),
        'title': artistObj.getName(),
        'tags' : artistObj.getTags(),
        'news': getArtistNews(5, str(artistObj.getName())),
        'lengthNews': len(getArtistNews(5, str(artistObj.getName()))),
    }

    return render(request, 'artist.html', tparams)

def news(request):
    assert isinstance(request, HttpRequest)

    news = getAllNews()

    tparams = {
        'news' : news,

    }
    return render(request, 'news.html', tparams)