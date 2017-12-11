import json
from urllib.request import urlopen, quote

YOUTUBE_API_KEY = 'AIzaSyCOnP9A04cW6GrUPdsIC5Hd7_vplDpVVaA'
YOUTUBE_ENDPOINT = 'https://www.googleapis.com/youtube/v3/search?part=snippet&q='

def getYoutubeVideoID(artist, song):
    url = urlopen(YOUTUBE_ENDPOINT + quote(artist) + quote(song) + '&key=' + YOUTUBE_API_KEY, timeout=10)

    data = json.loads(url.read().decode("utf-8"))

    for video in data['items']:
        title = str(video['snippet']['title']).strip()
        title1 = str(artist) + "-" + str(song)
        title2 = str(artist) + " - " + str(song)
        title3 = str(artist) + " -" + str(song)
        title4 = str(artist) + str(song)
        title5 = str(song) + " - " + str(artist)
        title6 = str(song) + " -" + str(artist)
        title7 = str(song) + str(artist)

        print("\n")
        print("Expected: \n\t" + title1)
        print("\t" + title2)
        print("\t" + title3)
        print("\t" + title4)
        print("Title: " + title)

        if title1.lower() in title.lower():
            return video['id']['videoId']
        elif title2.lower() in title.lower():
            return video['id']['videoId']
        elif title3.lower() in title.lower():
            return video['id']['videoId']
        elif title4.lower() in title.lower():
            return video['id']['videoId']
        elif title5.lower() in title.lower():
            return video['id']['videoId']
        elif title6.lower() in title.lower():
            return video['id']['videoId']
        elif title7.lower() in title.lower():
            return video['id']['videoId']

        if str(artist).lower() in str(video['snippet']['channelTitle']).lower():
            return video['id']['videoId']

    return None