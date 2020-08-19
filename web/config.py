from prediksicovidjatim import database
from prediksicovidjatim.data.model import ModelDataRepo
from django.apps import AppConfig

class WebConfig(AppConfig):
    name = 'web'
    verbose_name = "Prediksi Covid Jatim"
    def ready(self):
        database.init()
        ModelDataRepo.init_weights()