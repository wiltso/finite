from django.contrib import admin
from .models import Profile, Settings
# Register your models here.

lista = [Profile, Settings]
admin.site.register(lista)
