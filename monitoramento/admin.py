from django.contrib import admin
from .models import Leitura, Perfil, Sensor
admin.site.register(Perfil)
admin.site.register(Sensor)
admin.site.register(Leitura)

