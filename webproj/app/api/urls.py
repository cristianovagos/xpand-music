# URLs of Last.fm API

######################
# BASE CONFIGS
#

def getBaseURL():
    return "http://ws.audioscrobbler.com/2.0/?method="

def getAPIKey():
    return "32f8947b156b3993b3ff9159b81f4667"

def getAPIKeyText():
    return "&api_key=" + getAPIKey()

######################
# ALBUMS
#
# mbid: the album ID
# artist: artist name
# album: album name
# limit: number of results to fetch per page
# page: page number to fetch

def getAlbumInfoIDURL(mbid):
    return getBaseURL() + "album.getinfo" + getAPIKeyText() + "&mbid=" + mbid

def getAlbumInfoURL(artist, album):
    return getBaseURL() + "album.getinfo" + getAPIKeyText() + "&artist=" + artist + "&album=" + album

def getAlbumTopTagsIDURL(mbid):
    return getBaseURL() + "album.gettoptags" + getAPIKeyText() + "&mbid=" + mbid

def getAlbumTopTagsURL(artist, album):
    return getBaseURL() + "album.gettoptags" + getAPIKeyText() + "&artist=" + artist + "&album=" + album

def getAlbumSearchURL(album, limit=None, page=None):
    if limit and page:
        if not isinstance(limit, int) or not isinstance(page, int):
            raise TypeError('Limit or Page should be int type!')
        return getBaseURL() + "album.search" + getAPIKeyText() + "&album=" + album + "&limit=" + str(limit) + "&page=" + str(page)
    if limit:
        if not isinstance(limit, int):
            raise TypeError('Limit should be int type!')
        return getBaseURL() + "album.search" + getAPIKeyText() + "&album=" + album + "&limit=" + str(limit)
    if page:
        if not isinstance(page, int):
            raise TypeError('Page should be int type!')
        return getBaseURL() + "album.search" + getAPIKeyText() + "&album=" + album + "&page=" + str(page)
    return getBaseURL() + "album.search" + getAPIKeyText() + "&album=" + album

######################
# ARTISTS
#
# mbid: the Artist mbid
# artist: the Artist name
# limit: number of results to fetch per page
# page: page number to fetch

def getArtistInfoIDURL(mbid):
    return getBaseURL() + "artist.getinfo" + getAPIKeyText() + "&mbid=" + mbid

def getArtistInfoURL(artist):
    return getBaseURL() + "artist.getinfo" + getAPIKeyText() + "&artist=" + artist

def getArtistSimilarIDURL(mbid):
    return getBaseURL() + "artist.getsimilar" + getAPIKeyText() + "&mbid=" + mbid

def getArtistSimilarURL(artist):
    return getBaseURL() + "artist.getsimilar" + getAPIKeyText() + "&artist=" + artist

def getArtistTopTracksIDURL(mbid, limit=None, page=None):
    if limit and page:
        if not isinstance(limit, int) or not isinstance(page, int):
            raise TypeError('Limit or Page should be int type!')
        return getBaseURL() + "artist.gettoptracks" + getAPIKeyText() + "&mbid=" + mbid + "&limit=" + str(limit) + "&page=" + str(page)
    if limit:
        if not isinstance(limit, int):
            raise TypeError('Limit should be int type!')
        return getBaseURL() + "artist.gettoptracks" + getAPIKeyText() + "&mbid=" + mbid + "&limit=" + str(limit)
    if page:
        if not isinstance(page, int):
            raise TypeError('Page should be int type!')
        return getBaseURL() + "artist.gettoptracks" + getAPIKeyText() + "&mbid=" + mbid + "&page=" + str(page)
    return getBaseURL() + "artist.gettoptracks" + getAPIKeyText() + "&mbid=" + mbid

def getArtistTopTracksURL(artist, limit=None, page=None):
    if limit and page:
        if not isinstance(limit, int) or not isinstance(page, int):
            raise TypeError('Limit or Page should be int type!')
        return getBaseURL() + "artist.gettoptracks" + getAPIKeyText() + "&artist=" + artist + "&limit=" + str(limit) + "&page=" + str(page)
    if limit:
        if not isinstance(limit, int):
            raise TypeError('Limit should be int type!')
        return getBaseURL() + "artist.gettoptracks" + getAPIKeyText() + "&artist=" + artist + "&limit=" + str(limit)
    if page:
        if not isinstance(page, int):
            raise TypeError('Page should be int type!')
        return getBaseURL() + "artist.gettoptracks" + getAPIKeyText() + "&artist=" + artist + "&page=" + str(page)
    return getBaseURL() + "artist.gettoptracks" + getAPIKeyText() + "&artist=" + artist

def getArtistTopAlbumsIDURL(mbid, limit=None, page=None):
    if limit and page:
        if not isinstance(limit, int) or not isinstance(page, int):
            raise TypeError('Limit or Page should be int type!')
        return getBaseURL() + "artist.gettopalbums" + getAPIKeyText() + "&mbid=" + mbid + "&limit=" + str(limit) + "&page=" + str(page)
    if limit:
        if not isinstance(limit, int):
            raise TypeError('Limit should be int type!')
        return getBaseURL() + "artist.gettopalbums" + getAPIKeyText() + "&mbid=" + mbid + "&limit=" + str(limit)
    if page:
        if not isinstance(page, int):
            raise TypeError('Page should be int type!')
        return getBaseURL() + "artist.gettopalbums" + getAPIKeyText() + "&mbid=" + mbid + "&page=" + str(page)
    return getBaseURL() + "artist.gettopalbums" + getAPIKeyText() + "&mbid=" + mbid

def getArtistTopAlbumsURL(artist, limit=None, page=None):
    if limit and page:
        if not isinstance(limit, int) or not isinstance(page, int):
            raise TypeError('Limit or Page should be int type!')
        return getBaseURL() + "artist.gettopalbums" + getAPIKeyText() + "&artist=" + artist + "&limit=" + str(limit) + "&page=" + str(page)
    if limit:
        if not isinstance(limit, int):
            raise TypeError('Limit should be int type!')
        return getBaseURL() + "artist.gettopalbums" + getAPIKeyText() + "&artist=" + artist + "&limit=" + str(limit)
    if page:
        if not isinstance(page, int):
            raise TypeError('Page should be int type!')
        return getBaseURL() + "artist.gettopalbums" + getAPIKeyText() + "&artist=" + artist + "&page=" + str(page)
    return getBaseURL() + "artist.gettopalbums" + getAPIKeyText() + "&artist=" + artist

def getArtistTopTagsIDURL(mbid):
    return getBaseURL() + "artist.gettoptags" + getAPIKeyText() + "&mbid=" + mbid

def getArtistTopTagsURL(artist):
    return getBaseURL() + "artist.gettoptags" + getAPIKeyText() + "&artist=" + artist

def getArtistSearchIDURL(mbid, limit=None, page=None):
    if limit and page:
        if not isinstance(limit, int) or not isinstance(page, int):
            raise TypeError('Limit or Page should be int type!')
        return getBaseURL() + "artist.search" + getAPIKeyText() + "&mbid=" + mbid + "&limit=" + str(limit) + "&page=" + str(page)
    if limit:
        if not isinstance(limit, int):
            raise TypeError('Limit should be int type!')
        return getBaseURL() + "artist.search" + getAPIKeyText() + "&mbid=" + mbid + "&limit=" + str(limit)
    if page:
        if not isinstance(page, int):
            raise TypeError('Page should be int type!')
        return getBaseURL() + "artist.search" + getAPIKeyText() + "&mbid=" + mbid + "&page=" + str(page)
    return getBaseURL() + "artist.search" + getAPIKeyText() + "&mbid=" + mbid

def getArtistSearchURL(artist, limit=None, page=None):
    if limit and page:
        if not isinstance(limit, int) or not isinstance(page, int):
            raise TypeError('Limit or Page should be int type!')
        return getBaseURL() + "artist.search" + getAPIKeyText() + "&artist=" + artist + "&limit=" + str(limit) + "&page=" + str(page)
    if limit:
        if not isinstance(limit, int):
            raise TypeError('Limit should be int type!')
        return getBaseURL() + "artist.search" + getAPIKeyText() + "&artist=" + artist + "&limit=" + str(limit)
    if page:
        if not isinstance(page, int):
            raise TypeError('Page should be int type!')
        return getBaseURL() + "artist.search" + getAPIKeyText() + "&artist=" + artist + "&page=" + str(page)
    return getBaseURL() + "artist.search" + getAPIKeyText() + "&artist=" + artist

######################
# CHARTS
#
# limit: number of results to fetch per page
# page: page number to fetch

def getTopArtistsURL(limit=None, page=None):
    if limit and page:
        if not isinstance(limit, int) or not isinstance(page, int):
            raise TypeError('Limit or Page should be int type!')
        return getBaseURL() + "chart.gettopartists" + getAPIKeyText() + "&limit=" + str(limit) + "&page=" + str(page)
    if limit:
        if not isinstance(limit, int):
            raise TypeError('Limit should be int type!')
        return getBaseURL() + "chart.gettopartists" + getAPIKeyText() + "&limit=" + str(limit)
    if page:
        if not isinstance(page, int):
            raise TypeError('Page should be int type!')
        return getBaseURL() + "chart.gettopartists" + getAPIKeyText() + "&page=" + str(page)
    return getBaseURL() + "chart.gettopartists" + getAPIKeyText()

def getTopTagsURL(limit=None, page=None):
    if limit and page:
        if not isinstance(limit, int) or not isinstance(page, int):
            raise TypeError('Limit or Page should be int type!')
        return getBaseURL() + "chart.gettoptags" + getAPIKeyText() + "&limit=" + str(limit) + "&page=" + str(page)
    if limit:
        if not isinstance(limit, int):
            raise TypeError('Limit should be int type!')
        return getBaseURL() + "chart.gettoptags" + getAPIKeyText() + "&limit=" + str(limit)
    if page:
        if not isinstance(page, int):
            raise TypeError('Page should be int type!')
        return getBaseURL() + "chart.gettoptags" + getAPIKeyText() + "&page=" + str(page)
    return getBaseURL() + "chart.gettoptags" + getAPIKeyText()

def getTopTracksURL(limit=None, page=None):
    if limit and page:
        if not isinstance(limit, int) or not isinstance(page, int):
            raise TypeError('Limit or Page should be int type!')
        return getBaseURL() + "chart.gettoptracks" + getAPIKeyText() + "&limit=" + str(limit) + "&page=" + str(page)
    if limit:
        if not isinstance(limit, int):
            raise TypeError('Limit should be int type!')
        return getBaseURL() + "chart.gettoptracks" + getAPIKeyText() + "&limit=" + str(limit)
    if page:
        if not isinstance(page, int):
            raise TypeError('Page should be int type!')
        return getBaseURL() + "chart.gettoptracks" + getAPIKeyText() + "&page=" + str(page)
    return getBaseURL() + "chart.gettoptracks" + getAPIKeyText()


######################
# GEO
#
# limit: number of results to fetch per page
# page: page number to fetch

def getGeoTopArtistsURL(country, limit=None, page=None):
    if limit and page:
        if not isinstance(limit, int) or not isinstance(page, int):
            raise TypeError('Limit or Page should be int type!')
        return getBaseURL() + "geo.gettopartists" + getAPIKeyText() + "&country=" + country + "&limit=" + str(limit) + "&page=" + str(page)
    if limit:
        if not isinstance(limit, int):
            raise TypeError('Limit should be int type!')
        return getBaseURL() + "geo.gettopartists" + getAPIKeyText() + "&country=" + country + "&limit=" + str(limit)
    if page:
        if not isinstance(page, int):
            raise TypeError('Page should be int type!')
        return getBaseURL() + "geo.gettopartists" + getAPIKeyText() + "&country=" + country + "&page=" + str(page)
    return getBaseURL() + "geo.gettopartists" + getAPIKeyText() + "&country=" + country


def getGeoTopTracksURL(country, limit=None, page=None):
    if limit and page:
        if not isinstance(limit, int) or not isinstance(page, int):
            raise TypeError('Limit or Page should be int type!')
        return getBaseURL() + "geo.gettoptracks" + getAPIKeyText() + "&country=" + country + "&limit=" + str(limit) + "&page=" + str(page)
    if limit:
        if not isinstance(limit, int):
            raise TypeError('Limit should be int type!')
        return getBaseURL() + "geo.gettoptracks" + getAPIKeyText() + "&country=" + country + "&limit=" + str(limit)
    if page:
        if not isinstance(page, int):
            raise TypeError('Page should be int type!')
        return getBaseURL() + "geo.gettoptracks" + getAPIKeyText() + "&country=" + country + "&page=" + str(page)
    return getBaseURL() + "geo.gettoptracks" + getAPIKeyText() + "&country=" + country


######################
# TAG
#
# limit: number of results to fetch per page
# page: page number to fetch

def getTagInfoURL(tag):
    return getBaseURL() + "tag.getinfo" + getAPIKeyText() + "&tag=" + tag

def getTagSimilarURL(tag):
    return getBaseURL() + "tag.getsimilar" + getAPIKeyText() + "&tag=" + tag

def getTagTopAlbumsURL(tag, limit=None, page=None):
    if limit and page:
        if not isinstance(limit, int) or not isinstance(page, int):
            raise TypeError('Limit or Page should be int type!')
        return getBaseURL() + "tag.gettopalbums" + getAPIKeyText() + "&tag=" + tag + "&limit=" + str(limit) + "&page=" + str(page)
    if limit:
        if not isinstance(limit, int):
            raise TypeError('Limit should be int type!')
        return getBaseURL() + "tag.gettopalbums" + getAPIKeyText() + "&tag=" + tag + "&limit=" + str(limit)
    if page:
        if not isinstance(page, int):
            raise TypeError('Page should be int type!')
        return getBaseURL() + "tag.gettopalbums" + getAPIKeyText() + "&tag=" + tag + "&page=" + str(page)
    return getBaseURL() + "tag.gettopalbums" + getAPIKeyText() + "&tag=" + tag

def getTagTopArtistsURL(tag, limit=None, page=None):
    if limit and page:
        if not isinstance(limit, int) or not isinstance(page, int):
            raise TypeError('Limit or Page should be int type!')
        return getBaseURL() + "tag.gettopartists" + getAPIKeyText() + "&tag=" + tag + "&limit=" + str(limit) + "&page=" + str(page)
    if limit:
        if not isinstance(limit, int):
            raise TypeError('Limit should be int type!')
        return getBaseURL() + "tag.gettopartists" + getAPIKeyText() + "&tag=" + tag + "&limit=" + str(limit)
    if page:
        if not isinstance(page, int):
            raise TypeError('Page should be int type!')
        return getBaseURL() + "tag.gettopartists" + getAPIKeyText() + "&tag=" + tag + "&page=" + str(page)
    return getBaseURL() + "tag.gettopartists" + getAPIKeyText() + "&tag=" + tag

def getTagTopTagsURL(tag, limit=None, page=None):
    if limit and page:
        if not isinstance(limit, int) or not isinstance(page, int):
            raise TypeError('Limit or Page should be int type!')
        return getBaseURL() + "tag.gettoptags" + getAPIKeyText() + "&tag=" + tag + "&limit=" + str(limit) + "&page=" + str(page)
    if limit:
        if not isinstance(limit, int):
            raise TypeError('Limit should be int type!')
        return getBaseURL() + "tag.gettoptags" + getAPIKeyText() + "&tag=" + tag + "&limit=" + str(limit)
    if page:
        if not isinstance(page, int):
            raise TypeError('Page should be int type!')
        return getBaseURL() + "tag.gettoptags" + getAPIKeyText() + "&tag=" + tag + "&page=" + str(page)
    return getBaseURL() + "tag.gettoptags" + getAPIKeyText() + "&tag=" + tag

def getTagTopTracksURL(tag, limit=None, page=None):
    if limit and page:
        if not isinstance(limit, int) or not isinstance(page, int):
            raise TypeError('Limit or Page should be int type!')
        return getBaseURL() + "tag.gettoptracks" + getAPIKeyText() + "&tag=" + tag + "&limit=" + str(limit) + "&page=" + str(page)
    if limit:
        if not isinstance(limit, int):
            raise TypeError('Limit should be int type!')
        return getBaseURL() + "tag.gettoptracks" + getAPIKeyText() + "&tag=" + tag + "&limit=" + str(limit)
    if page:
        if not isinstance(page, int):
            raise TypeError('Page should be int type!')
        return getBaseURL() + "tag.gettoptracks" + getAPIKeyText() + "&tag=" + tag + "&page=" + str(page)
    return getBaseURL() + "tag.gettoptracks" + getAPIKeyText() + "&tag=" + tag

def getTagWeeklyChartListURL(tag):
    return getBaseURL() + "tag.getweeklychartlist" + getAPIKeyText() + "&tag=" + tag


######################
# TRACKS
#
# mbid: the Artist mbid
# artist: the Artist name
# limit: number of results to fetch per page
# page: page number to fetch

def getTrackInfoIDURL(mbid):
    return getBaseURL() + "track.getinfo" + getAPIKeyText() + "&mbid=" + mbid

def getTrackInfoURL(track, artist):
    return getBaseURL() + "track.getinfo" + getAPIKeyText() + "&artist=" + artist + "&track=" + track

def getTrackSimilarIDURL(mbid, limit=None):
    if limit:
        if not isinstance(limit, int):
            raise TypeError('Limit should be int type!')
        return getBaseURL() + "track.getsimilar" + getAPIKeyText() + "&mbid=" + mbid + "&limit=" + str(limit)
    return getBaseURL() + "track.getsimilar" + getAPIKeyText() + "&mbid=" + mbid

def getTrackSimilarURL(track, artist, limit=None):
    if limit:
        if not isinstance(limit, int):
            raise TypeError('Limit should be int type!')
        return getBaseURL() + "track.getsimilar" + getAPIKeyText() + "&artist=" + artist + "&track=" + track + "&limit=" + str(limit)
    return getBaseURL() + "track.getsimilar" + getAPIKeyText() + "&artist=" + artist + "&track=" + track

def getTrackTagsIDURL(mbid):
    return getBaseURL() + "track.gettags" + getAPIKeyText() + "&mbid=" + mbid

def getTrackTagsURL(track, artist):
    return getBaseURL() + "track.gettags" + getAPIKeyText() + "&artist=" + artist + "&track=" + track

def getTrackTopTagsIDURL(mbid):
    return getBaseURL() + "track.gettoptags" + getAPIKeyText() + "&mbid=" + mbid

def getTrackTopTagsURL(track, artist):
    return getBaseURL() + "track.gettoptags" + getAPIKeyText() + "&artist=" + artist + "&track=" + track

def getTrackSearchURL(track, artist=None, limit=None, page=None):
    if limit and page:
        if not isinstance(limit, int) or not isinstance(page, int):
            raise TypeError('Limit or Page should be int type!')
        else:
            result = getBaseURL() + "track.search" + getAPIKeyText() + "&track=" + track + "&page=" + str(
                page) + "&limit=" + str(limit)
            return result + "&artist=" + artist if artist else result
    if limit:
        if not isinstance(limit, int):
            raise TypeError('Limit should be int type!')
        else:
            result = getBaseURL() + "track.search" + getAPIKeyText() + "&track=" + track + "&limit=" + str(limit)
            return result + "&artist=" + artist if artist else result
    if page:
        if not isinstance(page, int):
            raise TypeError('Page should be int type!')
        else:
            result = getBaseURL() + "track.search" + getAPIKeyText() + "&track=" + track + "&page=" + str(page)
            return result + "&artist=" + artist if artist else result
    result = getBaseURL() + "track.search" + getAPIKeyText() + "&track=" + track
    return result + "&artist=" + artist if artist else result
