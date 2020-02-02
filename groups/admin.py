from django.contrib import admin
from .models import Friendgroup, Groupmembers

lista = [Friendgroup, Groupmembers]
admin.site.register(lista)
