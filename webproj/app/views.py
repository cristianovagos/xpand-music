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
        'title':'Index',
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
            img = y.find('image').text
            aux.append(img)
            result.append(aux)

    tparams = {
        'title':'teste',
        'year':datetime.now().year,
        'array' :result,
    }
    return render(request, 'top.html', tparams)




def albumInfo(request):
                                     # static test
    albumNameArg = 'Believe'
    artistNameArg = 'Cher'

    assert isinstance(request, HttpRequest)

    file = urlopen(
        "http://ws.audioscrobbler.com/2.0/?method=album.getinfo&api_key=32f8947b156b3993b3ff9159b81f4667&artist=" + artistNameArg + "&album=" + albumNameArg + "")
    tree = ET.parse(file)
    root = tree.getroot()
    result = {}
    tracks = []
    for x in root.findall('album'):
        album = x.find('name').text
        artist = x.find('artist').text
        listeners = x.find('listeners').text
        playcount = x.find('playcount').text
        image = x.find('image').text
        for y in x.findall('tracks/track'):  # tracks
            tracks.append(y.find('name').text)

        '''
        result['album'] = album
        result['artist'] = artist
        result['listeners'] = listeners
        result['playcount'] = playcount
        result['tracks'] = tracks
        '''

    tparams = {
        'title': album + ' by ' + artist,
        'year': datetime.now().year,
        'image': image,
        'listeners' : listeners,
        'playcount' : playcount,
        'dict': tracks,
    }
    return render(request, 'albumInfo.html', tparams)