from http.client import HTTPResponse
import xml.etree.ElementTree as ET
from urllib.parse import quote
from urllib.request import urlopen
from urllib.error import HTTPError
from webproj.app.model.artist import Artist
from webproj.app.model.track import Track
from webproj.app.model.album import Album
from webproj.app.api.urls import getTopArtistsURL

#x = Artist("Cher")
#x = Track("Cher", "Believe", None)
#x = Album("Believe", "Cher")

#print(x)
artistSearch = "cher"

url = "http://ws.audioscrobbler.com/2.0/?method=artist.search&artist=" + artistSearch + "&api_key=32f8947b156b3993b3ff9159b81f4667&limit=2&page=1"

print(url)

file = urlopen( url )
straux = str(file.read().decode())
print(straux)
juntar = '<results for="' + artistSearch + '" xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">'

straux = straux.replace('<results for="' + artistSearch + '">', juntar)

# print(straux)

root = ET.fromstring(straux)
result = []

for x in root.findall('results/artistmatches/artist'):
    aux = []
    aux.append(str(x.find('name').text))
    aux.append(x.find('image[@size="extralarge"]').text)
    result.append(aux)
print(result)
