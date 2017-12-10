"""webproj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin, auth
from app import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^album/(?P<artist>[\w|\W]+)/(?P<album>[\w|\W]+)$', views.album, name='album'),
    url(r'^artist/(?P<artist>[\w|\W]+)$', views.artist, name='artist'),
    url(r'^tag/(?P<tag>[\w|\W]+)$', views.tag, name='tag'),
    url(r'^news/$', views.news, name='news'),
    url(r'^search/$', views.search, name='search'),
    url(r'^top/tags/$', views.topArtistsByTag, name='topTags'),
    url(r'^top/countries/$', views.topArtistsByCountry, name='topCountries'),
    # url(r'^top/tags/(?P<page>[0-9]+)$', views.topTagsPage),
    url(r'^top/artists/$', views.topArtists, name='topArtists'),
    url(r'^top/artists/(?P<page>[0-9]+)$', views.topArtistsPage, name='topArtistsPage'),
    url(r'^top/tracks/$', views.topTracks, name='topTracks'),
    url(r'^top/tracks/(?P<page>[0-9]+)$', views.topTracksPage, name='topTracksPage'),
]
