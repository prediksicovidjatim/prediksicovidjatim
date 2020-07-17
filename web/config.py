from core import database
from django.apps import AppConfig

class WebConfig(AppConfig):
    name = 'web'
    verbose_name = "Prediksi Covid Jatim"
    def ready(self):
        database.init()