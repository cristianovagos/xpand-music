# xPand Music

A project made for EDC (Engenharia de Dados e Conhecimento) course of MIECT, at DETI-UA (University of Aveiro).

Our main goal for this project is to put in practise the subjects learned throughout the course, mainly Django and the use of XML and XML related tools and techniques, such as XML Schema, XSLT, XPath, XQuery and XUpdate as well as the use of a XML database (in our case we chose BaseX) to store and retrieve data from a XML document.

So, xPand (as we agreed to call this project) uses the Last.fm XML API to fetch data from artists, tracks, albums and charts to collect data, and then transforms the XML fetched to our structure, validates it according to our XML Schema to make sure it has the structure we want, and then stores the data collected on the BaseX database.

The data is fetched from API only when the data itself is not present within the database. When it fetches and adds the data, the app will then display the data in a pretty way using also Bootstrap in the web design for Artists, Albums, Tags and Charts.

NOTE: This project may be incomplete and it surely needs more attention and features, but that's what we could do for the deadline provided of the course.

### Developers and collaborators:
- [Cristiano Vagos](http://github.com/cristianovagos)
- [André Rodrigues](http://github.com/suduaya)

### Installation
Install Python 3.6, BaseX, LXML and Django:
```sh
$ sudo apt-get install python3.6 basex python3-lxml
$ pip3.6 install Django
```

### How to run
Initialize the BaseX Server:
```sh
$ basexserver
```

Run Django server on project folder:
```sh
$ python3.6 manage.py runserver
```

Click on URL provided upon the last command execution, default is "127.0.0.1:8000"
