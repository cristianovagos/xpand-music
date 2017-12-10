# -*- coding: utf-8 -*-

from datetime import datetime
from urllib.request import quote
from .model.artist import Artist
from .model.album import Album
from .model.tag import Tag
from django.http import HttpRequest
from django.shortcuts import render, redirect
from .api.artists.artists import getTopArtists, getTopArtistsGraphDB, getTopArtistsCountriesGraphDB
from .api.searchs.search import searchArtist, searchAlbum
from .api.tracks.tracks import getTopTracks, getTopTracksGraphDB
from .api.news.news import *
from .forms import SearchForm, CommentForm
from .api.tags.tags import getTagTopArtists, getTagTopArtistsGraphDB, getTopTagsGraphDB
from .api.albums.albums import *
from .utils.countries import getCountriesGraphDB


# Create your views here.

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)

    tparams = {
        'title':'xPand - Your music hub.',
        'topArtists' : getTopArtistsGraphDB(),
        'topTracks': getTopTracksGraphDB(),
        'news': getAllNews(6),
        'form': SearchForm()
    }
    return render(request, 'index.html', tparams)

def album(request, album, artist):
    assert isinstance(request, HttpRequest)

    artistObj = Artist(str(artist))
    albumObj = Album(str(album), str(artist))
    artistObj.fetchInfoGraphDB()

    if request.method == 'POST':
        if request.POST['form-type'] == 'comment-form':
            form = CommentForm(request.POST)

            if form.is_valid():
                text = str(request.POST['comment'])
                albumObj.storeComment('User', text)
                albumObj = Album(str(album), str(artist))
        elif request.POST['form-type'] == 'edit-form':
            edit = str(request.POST['editComment'])
            commentID = str(request.POST['commentID'])
            albumObj.changeComment(commentID, edit)
            albumObj = Album(str(album), str(artist))
        else:
            commentID = str(request.POST['commentID'])
            albumObj.deleteComment(commentID)
            albumObj = Album(str(album), str(artist))


    tparams = {
        'title' : 'xPand | "' + str(album) + '" by ' + str(artist),
        'album' : album,
        'artist': artist,
        'year': datetime.now().year,
        'image': albumObj.getImage(),
        'wiki': albumObj.getWikiShort(),
        'tags': albumObj.getTags(),
        'tracks': albumObj.getTracks(),
        'form' : SearchForm(),
        'commentForm': CommentForm(),
        'comments': albumObj.getComments(),
        'url' : 'album',
        'topAlbums' : artistObj.getTopAlbums(),
        'datePublished': albumObj.getDatePublished(),
        'age': albumObj.getAge(),
        'genres': albumObj.getGenres(),
        'recorders' : albumObj.getRecorders(),
        'producer': albumObj.getProducer(),
        'previousAlbum': albumObj.getPreviousAlbum(),
        'nextAlbum': albumObj.getNextAlbum(),
        'similarAlbums': albumObj.getSimilarAlbums(),
    }
    return render(request, 'album.html', tparams)

def tag(request, tag):
    assert isinstance(request, HttpRequest)

    tagObj = Tag(tag, max_items=5)

    tparams = {
        'title' : 'xPand | ' + str(tag),
        'tag' : tag,
        'form' : SearchForm(),
        'topAlbums': tagObj.getTopAlbums(),
        'topTracks': tagObj.getTopTracks(),
        'topArtists': tagObj.getTopArtists(),
        'wiki': tagObj.getWikiShort(),
    }

    return render(request, 'tag.html', tparams)

def artist(request, artist):
    assert isinstance(request, HttpRequest)

    artistObj = Artist(artist)

    if request.method == 'POST':
        if request.POST['form-type'] == 'comment-form':
            form = CommentForm(request.POST)

            if form.is_valid():
                text = str(request.POST['comment'])
                artistObj.storeComment('User', text)
                artistObj = Artist(artist)
        elif request.POST['form-type'] == 'edit-form':
            edit = str(request.POST['editComment'])
            commentID = str(request.POST['commentID'])
            artistObj.changeComment(commentID, edit)
            artistObj = Artist(artist)
        else:
            commentID = str(request.POST['commentID'])
            artistObj.deleteComment(commentID)
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
        'title': 'xPand | ' + artistObj.getName(),
        'tags' : artistObj.getTags(),
        'news': getArtistNews(5, str(artistObj.getName())),
        'lengthNews': len(getArtistNews(5, str(artistObj.getName()))),
        'form': SearchForm(),
        'commentForm': CommentForm(),
        'comments': artistObj.getComments(),
        'url' : 'artist',
        'country' : artistObj.getCountry(),
        'countryCode': artistObj.getCountryCode(),
        'members': artistObj.getMembers(),
        'website': artistObj.getWebsite(),
        'recorders': artistObj.getRecorders(),
        'occupations': artistObj.getOccupation(),
        'gender': artistObj.getGender(),
        'genres': artistObj.getGenres(),
        'yearFounded': artistObj.getYearFounded(),
        'givenName': artistObj.getGivenName(),
        'birthDate': artistObj.getBirthDate(),
        'age' : artistObj.getAge(),
        'bands' : artistObj.getBands(),
    }

    return render(request, 'artist.html', tparams)

def news(request):
    assert isinstance(request, HttpRequest)

    tparams = {
        'title': 'xPand | News',
        'news' : getAllNews(18),
        'lastnews': getAllNews(6),
        'form' : SearchForm()
    }
    return render(request, 'news.html', tparams)

def search(request):
    assert isinstance(request, HttpRequest)

    if request.method == 'POST':
        form = SearchForm(request.POST)

        if form.is_valid():
            searching = str(request.POST['searchCriteria'])
            artistSearch = searchArtist(searching)
            albumSearch = searchAlbum(searching)

            tparams = {
                'title': 'xPand | Search by "' + searching + '"',
                'artistSearch'   : artistSearch,
                'albumSearch'    : albumSearch,
                'form'           : SearchForm(),
                'search'         : searching
            }

            return render(request, 'searchResult.html', tparams)
    return render(request, 'searchResult.html',
                  {
                      'title': 'xPand - Your music hub.',
                      'form'    : SearchForm(),
                      'search'  : None
                  })

def topArtistsByTag(request):
    assert isinstance(request, HttpRequest)

    artists = []
    # tags = topTags()
    tags = getTopTagsGraphDB(num=10)
    for tag in tags:
        # artists.append(getTagTopArtists(tag))
        artists.append(getTagTopArtistsGraphDB(tag))

    tparams = {
        'title'      : 'xPand | Top Tags',
        'topArtists' : artists,
        'tags'       : tags,
        'form'       : SearchForm()
    }
    return render(request, 'toptags.html', tparams)

def topArtistsByCountry(request):
    assert isinstance(request, HttpRequest)

    artists = []
    countries = getCountriesGraphDB(num=10)
    for country in countries:
        artists.append(getTopArtistsCountriesGraphDB(str(country[0])))

    tparams = {
        'title'      : 'xPand | Top Countries',
        'topArtists' : artists,
        'countries'  : countries,
        'form'       : SearchForm()
    }

    return render(request, 'topcountries.html', tparams)

def topArtists(request):
    assert isinstance(request, HttpRequest)

    tparams = {
        'title': 'xPand | Top Artists',
        'topArtists': getTopArtistsGraphDB(num=50),
        # 'topArtists': getTopArtists(num=50),
        'form': SearchForm(),
        'page': 1
    }

    return render(request, 'topartists.html', tparams)

def topArtistsPage(request, page):
    assert isinstance(request, HttpRequest)

    tparams = {
        'title': 'xPand | Top Artists',
        'topArtists': getTopArtistsGraphDB(num=50, page=int(page)),
        # 'topArtists': getTopArtists(num=50, page=int(page)),
        'form': SearchForm(),
        'page': int(page)
    }

    return render(request, 'topartists.html', tparams)

def topTracks(request):
    assert isinstance(request, HttpRequest)

    tparams = {
        'title': 'xPand | Top Tracks',
        'topTracks': getTopTracksGraphDB(num=50),
        # 'topTracks': getTopTracks(num=50),
        'form': SearchForm(),
        'page': 1
    }

    return render(request, 'toptracks.html', tparams)

def topTracksPage(request, page):
    assert isinstance(request, HttpRequest)

    tparams = {
        'title': 'xPand | Top Tracks',
        'topTracks': getTopTracksGraphDB(num=50, page=int(page)),
        # 'topTracks': getTopTracks(num=50, page=int(page)),
        'form': SearchForm(),
        'page': int(page)
    }

    return render(request, 'toptracks.html', tparams)