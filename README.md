# xPand Music

A project made for EDC (Engenharia de Dados e Conhecimento) course of MIECT, at DETI-UA (University of Aveiro).
The same subject and project was used for two parts, using two distinct data representations: XML and RDF.

#### First part
Our main goal for this project is to put in practise the subjects learned throughout the first part of this course, mainly the use of Django and of XML and XML related tools and XML' derivated technologies such as XML Schema, XSLT, XPath, XQuery and XUpdate as well as the use of a XML database (in our case we chose BaseX) to store and retrieve data from a XML document.

Final commit to first part:
https://github.com/cristianovagos/xpand-music/commit/280aa473fa85eee3ea042b14cee52642dcdae030

#### Second part
In the second part, we switched the main data to RDF, and added more features related to RDF, such as inferences and other stuff that relate data to the data stored. For storage we used the triplestore GraphDB, and for URIs we used a dummy URI created for this purpose.

So, xPand Music (as we agreed to call this project, a way of Expanding Music knowledge) uses the Last.fm XML API to fetch data from artists, tracks, albums and charts to collect data, transforms the XML fetched to our structure using XSLT, validates it according to our XML Schema to make sure it has the structure we want, and then stores the data collected on the BaseX database.

The data is fetched from API only when the data itself is not present within the database. When it fetches and adds the data, the app will then display the data in a pretty way using also Bootstrap in the web design for Artists, Albums, Tags and Charts.

NOTE: This project may be incomplete and it surely needs more attention and features, but that's what we could do for the deadline provided of the course.

#### Grades
First part grade: 19/20
Second part grade: 20/20

### Developers and collaborators:
- [Cristiano Vagos](http://github.com/cristianovagos)
- [André Rodrigues](http://github.com/suduaya)

### Installation (First part)
Install Python 3.6, and Django:
```sh
$ sudo apt-get install python3.6 python3-lxml
$ pip3.6 install Django
```
Install GraphDB

### Installation (Second part)
Install Python 3.6, Django and GraphDB:
```sh
$ sudo apt-get install python3.6 basex python3-lxml
$ pip3.6 install Django
```

### How to run (First part)
Initialize the BaseX Server:
```sh
$ basexserver
```

### How to run (Second part)
Run GraphDB, create 'xpand-music' graph.

Run Django server on project folder:
```sh
$ python3.6 manage.py runserver
```

Click on URL provided upon the last command execution, default is "127.0.0.1:8000"
