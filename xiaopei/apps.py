from django.apps import AppConfig
from django.core.cache import cache
import codecs
import json
import os

class MyAppConfig(AppConfig):
    name = 'xiaopei'

    def ready(self):
        return
