from django.contrib import admin
from .models import Timmar, ExcludeTimmar, Links, Schools_hours, Schools, Exclude_schools_hours

lista = [Timmar, ExcludeTimmar, Links, Schools_hours, Schools, Exclude_schools_hours]
admin.site.register(lista)
