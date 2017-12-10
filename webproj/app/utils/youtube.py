import json
from urllib.request import urlopen, quote

YOUTUBE_API_KEY = 'AIzaSyCOnP9A04cW6GrUPdsIC5Hd7_vplDpVVaA'
YOUTUBE_ENDPOINT = 'https://www.googleapis.com/youtube/v3/search?part=snippet&q='

def getVideoID(artist, song):
    url = urlopen(YOUTUBE_ENDPOINT + quote(quote(artist) + ' - ' + quote(song)) + '&key=' + YOUTUBE_API_KEY)

    data = json.loads(url.read().decode("utf-8"))

    videoID = None
    for video in data['items']:
        videoID = video['id']['videoId']

        if str(artist).lower() in str(video['snippet']['channelTitle']).lower():
            return videoID
    return videoID