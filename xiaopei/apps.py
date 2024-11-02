from django.apps import AppConfig

class MyAppConfig(AppConfig):
    name = 'xiaopei'

    def ready(self):
        return