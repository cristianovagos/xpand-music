from urllib.request import urlopen
import xml.etree.ElementTree as ET

def getAllNews(num=25):
    file = urlopen(
        "http://www.music-news.com/rss/UK/news?includeCover=true")
    tree = ET.parse(file)
    root = tree.getroot()
    result = []

    i = 0
    for x in root.findall('channel/item'):
        if i >= num:
            break
        new = {}
        new['title'] = x.find('title').text
        new['description'] = x.find('description').text
        new['author'] = x.find('author').text
        new['pubDate'] = x.find('pubDate').text
        new['image'] = x.find('enclosure').attrib['url']
        new['link'] = x.find('link').text
        result.append(new)
        i+=1

    return result


def getArtistNews(num=5, artist=""):
    file = urlopen(
        "http://www.music-news.com/rss/UK/news?includeCover=true")
    tree = ET.parse(file)
    root = tree.getroot()
    result = []

    i = 0
    for x in root.findall('channel/item'):
        if i >= num:
            break
        new = {}
        if str(artist) in str(x.find('description').text):
            new['title'] = x.find('title').text
            new['description'] = x.find('description').text
            new['author'] = x.find('author').text
            new['pubDate'] = x.find('pubDate').text
            new['image'] = x.find('enclosure').attrib['url']
            new['link'] = x.find('link').text
            result.append(new)
            i+=1

    return result