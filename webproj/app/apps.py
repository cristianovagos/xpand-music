import os
from django.apps import AppConfig
from .db.create import *

class AppConfig(AppConfig):
    name = 'app'
