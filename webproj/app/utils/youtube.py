import json
from urllib.request import urlopen, quote

YOUTUBE_API_KEY = 'AIzaSyCOnP9A04cW6GrUPdsIC5Hd7_vplDpVVaA'
YOUTUBE_ENDPOINT = 'https://www.googleapis.com/youtube/v3/search?part=snippet&q='

def getYoutubeVideoID(artist, song):
    url = urlopen(YOUTUBE_ENDPOINT + quote(artist) + quote(" ") + quote(song) + '&key=' + YOUTUBE_API_KEY, timeout=20)
    print(YOUTUBE_ENDPOINT + quote(artist) + quote(" ") + quote(song) + '&key=' + YOUTUBE_API_KEY)

    data = json.loads(url.read().decode("utf-8"))

    artist = str(artist).replace(" - ", " ")
    song = str(song).replace(" - ", " ")
    song = song.replace("(", "")
    song = song.replace(")", "")

    for video in data['items']:
        title = str(video['snippet']['title']).strip()
        title = title.replace(" - ", " ")
        title = title.replace("(", "")
        title = title.replace(")", "")

        if artist.lower() in title.lower() and song.lower() in title.lower():
            try:
                return video['id']['videoId']
            except Exception:
                pass
    return None