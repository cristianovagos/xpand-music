# XPand Music

A project made for EDC (Engenharia de Dados e Conhecimento) course of MIECT, at DETI-UA (University of Aveiro).

Our goal is to put in practise the subjects learned throughout the course, mainly Django and the use of XML, XML Schema, XPath and XQuery, as well as the use of a XML database to populate data, and retrieve data from a external XML throughout the internet, such as a API.

So, xPand (as we agreed to call this project) uses Last.fm XML API to fetch data from artists, tracks, albums and charts to collect data, and stores the data collected on the BaseX database when fetched so it fetches data only when needed, displaying the data in a pretty way using also Bootstrap in the web design.

This project may be incomplete and it surely needs more attention and features, but that's what we could do for the deadline provided of the course.

### Developers and collaborators:
- Cristiano Vagos (http://github.com/cristianovagos)
- André Rodrigues (http://github.com/suduaya)

### Installation
Install Python 3.6, BaseX and Django:
```sh
$ sudo apt-get install basex
$ sudo apt-get install python3.6
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
