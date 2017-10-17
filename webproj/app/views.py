# -*- coding: utf-8 -*-

from datetime import datetime
from urllib.request import urlopen

from django.http import HttpRequest
from django.shortcuts import render

#from webproj.app.api.artists.artists import getArtistInfo


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




#def albumInfo(request, album, artist):
    #
    # assert isinstance(request, HttpRequest)
    #
    # file = urlopen(
    #     "http://ws.audioscrobbler.com/2.0/?method=album.getinfo&api_key=32f8947b156b3993b3ff9159b81f4667&artist=" + str(artist) + "&album=" + str(album) + "")
    # tree = ET.parse(file)
    # root = tree.getroot()
    # result = {}
    # tracks = []
    # for x in root.findall('album'):
    #     album = x.find('name').text
    #     artist = x.find('artist').text
    #     listeners = x.find('listeners').text
    #     playcount = x.find('playcount').text
    #     image = x.find('.//image[@size="mega"]').text
    #     for y in x.findall('tracks/track'):  # tracks
    #         track=[]
    #         track.append(y.find('name').text)
    #         dur = int(y.find('duration').text)/100
    #         track.append(dur)
    #         tracks.append(track)
    #
    # tparams = {
    #     'album': album,
    #     'artist':artist,
    #     'year': datetime.now().year,
    #     'image': image,
    #     'listeners' : listeners,
    #     'playcount' : playcount,
    #     'dict': tracks,
    #     'title': album,
    # }
    # return render(request, 'albumInfo.html', tparams)


#def artistInfo(request, artist):
    # funcao que retorna a informacao sobre o artista e respectivos artistas semelhantes
    # artist= "Eminem"
    #
    #
    # assert isinstance(request, HttpRequest)
    #
    # artistInfoResult = getArtistInfo(artist)
    #
    # tparams = {
    #     'summary' : artistInfoResult[0][0],    # bio, sumario
    #     'content' : artistInfoResult[0][1],    # bio, texto completo
    #     'image'   : artistInfoResult[0][2],    # imagem artista
    #     'name'    : bio[3],    # nome artista
    #     'similars': similars,  # 0- name artists, 1- image
    #     'topAlbums': topAlbums, # array de top albums
    #     'top5': top5,
    #     'songs5':songs5,
    #     'title' : bio[3],
    # }
    # return render(request, 'artistInfo.html', tparams)