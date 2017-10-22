# -*- coding: utf-8 -*-

from datetime import datetime
from urllib.request import urlopen
from .model.artist import Artist
from .model.album import Album
from django.http import HttpRequest
from django.shortcuts import render, redirect
from .api.artists.artists import getTopArtists
from .api.searchs.search import searchArtist, searchAlbum
from .api.tracks.tracks import getTopTracks
from .api.news.news import *
from .forms import SearchForm, CommentForm
from .api.tags.tags import *
#from webproj.app.api.artists.artists import getArtistInfo


# Create your views here.

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)

    tparams = {
        'title':'xPand',
        'message':'Your indexx page.',
        'year':datetime.now().year,
        'topArtists' : getTopArtists(),
        'topTracks': getTopTracks(),
        'news': getAllNews(5),
        'form': SearchForm()
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

def albumInfo(request, album, artist):
    assert isinstance(request, HttpRequest)

    albumObj = Album(str(album), str(artist))

    if request.method == 'POST':
        form = CommentForm(request.POST)

        if form.is_valid():
            text = str(request.POST['comment'])
            albumObj.storeComment('User', text)
            albumObj = Album(str(album), str(artist))

    tparams = {
        'album' : album,
        'artist': artist,
        'year': datetime.now().year,
        'image': albumObj.getImage(),
        'wiki': albumObj.getWikiShort(),
        'tags': albumObj.getTags(),
        'tracks': albumObj.getTracks(),
        'title': album,
        'form' : SearchForm(),
        'commentForm': CommentForm(),
        'comments': albumObj.getComments(),
        'url' : 'album'
    }
    return render(request, 'album.html', tparams)

def artistInfo(request, artist):
    assert isinstance(request, HttpRequest)

    artistObj = Artist(artist)

    if request.method == 'POST':
        form = CommentForm(request.POST)

        if form.is_valid():
            text = str(request.POST['comment'])
            artistObj.storeComment('User', text)
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
        'form': SearchForm(),
        'commentForm': CommentForm(),
        'comments': artistObj.getComments(),
        'url' : 'artist'
    }

    return render(request, 'artist.html', tparams)

def news(request):
    assert isinstance(request, HttpRequest)

    tparams = {
        'news' : getAllNews(),
        'form' : SearchForm()
    }
    return render(request, 'news.html', tparams)

def searchResult(request):
    assert isinstance(request, HttpRequest)

    if request.method == 'POST':
        form = SearchForm(request.POST)

        if form.is_valid():
            searching = str(request.POST['searchCriteria'])
            artistSearch = searchArtist(searching)
            albumSearch = searchAlbum(searching)

        tparams = {
            'artistSearch'   : artistSearch,
            'lenArtistSearch': len(artistSearch),
            'albumSearch'    : albumSearch,
            'lenAlbumSearch' : len(albumSearch),
            'form' : SearchForm()
        }
        return render(request, 'searchResult.html', tparams)
    else:
        return render(request, 'searchResult.html', {'form' : SearchForm()})

def top(request):
    assert isinstance(request, HttpRequest)

    artists = []
    tags =  topGenresArtists()
    for tag in tags:
        artists.append(getTagTopArtists(tag))

    tparams = {
        'topArtists' : artists,
        'tags'       : tags,
        'form': SearchForm()
    }
    return render(request, 'top.html', tparams)
